"""
PQC-Day and the Machine — Chapter 12
Pattern: RepositoryTools — 5 tools for the autonomous code analysis agent

This is a didactic example from the book, not production code.
See chapter 12 for full context and explanation.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional


class RepositoryTools:
    """Repository exploration tools for the agent."""

    IGNORE_DIRS = {
        '__pycache__', 'node_modules', '.git', '.svn', 'venv',
        '.venv', 'dist', 'build', '.idea', 'coverage', '.eggs'
    }

    def __init__(self, repo_path: str, max_file_size: int = 100_000):
        self.repo_path = Path(repo_path)
        self.max_file_size = max_file_size  # 100 KB default

    def get_tool_definitions(self) -> list:
        """Return the 5 tools in OpenAI function calling format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "List files and folders in a directory.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "default": "."},
                            "recursive": {"type": "boolean", "default": False}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read the content of a file.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "start_line": {"type": "integer"},
                            "end_line": {"type": "integer"}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_code",
                    "description": "Search for a text pattern or regex in source code.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pattern": {"type": "string"},
                            "path": {"type": "string"},
                            "is_regex": {"type": "boolean", "default": False},
                            "case_sensitive": {"type": "boolean", "default": False}
                        },
                        "required": ["pattern"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "find_crypto_usage",
                    "description": "Find cryptographic algorithm usage by type "
                                   "(rsa, aes, ecdsa, ecdh, dh, sha, md5, dsa, or all).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "crypto_type": {"type": "string", "default": "all"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_file_summary",
                    "description": "Get a structured summary of a file "
                                   "(classes, functions, imports).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"}
                        },
                        "required": ["path"]
                    }
                }
            },
        ]

    def execute_tool(self, tool_name: str, arguments: dict) -> dict:
        """Central dispatch: name -> Python method."""
        handlers = {
            "list_files":        self._list_files,
            "read_file":         self._read_file,
            "search_code":       self._search_code,
            "find_crypto_usage": self._find_crypto_usage,
            "get_file_summary":  self._get_file_summary,
        }
        handler = handlers.get(tool_name)
        if not handler:
            return {'success': False, 'error': f'Unknown tool: {tool_name}'}
        try:
            return handler(**arguments)
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _list_files(self, path: str = '.', recursive: bool = False) -> dict:
        """List files in a directory."""
        target = self.repo_path / path
        try:
            target.resolve().relative_to(self.repo_path.resolve())
        except ValueError:
            return {'success': False, 'error': 'Access denied: path outside repository'}

        if not target.exists():
            return {'success': False, 'error': f'Path not found: {path}'}

        items = []
        if recursive:
            for root, dirs, files in os.walk(target):
                dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
                for f in files:
                    rel = os.path.relpath(os.path.join(root, f), self.repo_path)
                    items.append({'type': 'file', 'path': rel})
        else:
            for item in sorted(target.iterdir()):
                if item.name in self.IGNORE_DIRS:
                    continue
                items.append({
                    'type': 'directory' if item.is_dir() else 'file',
                    'name': item.name,
                    'size': item.stat().st_size if item.is_file() else None
                })

        return {'success': True, 'result': {'items': items, 'count': len(items)}}

    def _read_file(self, path: str, start_line: int = None,
                   end_line: int = None) -> dict:
        """Read a file with mandatory path validation."""
        file_path = self.repo_path / path

        # Security validation: is the resolved path inside the repo?
        try:
            file_path.resolve().relative_to(self.repo_path.resolve())
        except ValueError:
            return {'success': False, 'error': 'Access denied: path outside repository'}

        if not file_path.exists():
            return {'success': False, 'error': f'File not found: {path}'}

        # Size validation: prevent reading huge files
        if file_path.stat().st_size > self.max_file_size:
            return {
                'success': False,
                'error': f'File too large: {file_path.stat().st_size} bytes'
            }

        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        if start_line or end_line:
            start = (start_line or 1) - 1
            end = end_line or len(lines)
            lines = lines[start:end]

        return {'success': True, 'result': {
            'path': path,
            'content': ''.join(lines),
            'total_lines': len(lines)
        }}

    def _search_code(self, pattern: str, path: str = None,
                     is_regex: bool = False,
                     case_sensitive: bool = False) -> dict:
        """Search for a pattern in source code files."""
        search_root = self.repo_path / (path or '.')
        flags = 0 if case_sensitive else re.IGNORECASE

        if is_regex:
            try:
                compiled = re.compile(pattern, flags)
            except re.error as e:
                return {'success': False, 'error': f'Invalid regex: {e}'}
        else:
            escaped = re.escape(pattern)
            compiled = re.compile(escaped, flags)

        matches = []
        for root, dirs, files in os.walk(search_root):
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
            for filename in files:
                if not any(filename.endswith(ext) for ext in
                           ['.py', '.js', '.ts', '.java', '.go', '.rs',
                            '.c', '.cpp', '.h', '.yaml', '.yml', '.json']):
                    continue
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        for i, line in enumerate(f, 1):
                            if compiled.search(line):
                                matches.append({
                                    'file': os.path.relpath(filepath, self.repo_path),
                                    'line': i,
                                    'match': line.strip()[:200]
                                })
                                if len(matches) >= 100:
                                    break
                except Exception:
                    continue
                if len(matches) >= 100:
                    break

        return {'success': True, 'result': {
            'pattern': pattern,
            'matches': matches,
            'total': len(matches),
            'truncated': len(matches) >= 100
        }}

    def _find_crypto_usage(self, crypto_type: str = "all") -> dict:
        """Find cryptographic usage with specialized patterns."""
        crypto_patterns = {
            'rsa':   [r'RSA\s*[\(\.]', r'rsa[-_]?key', r'PKCS1', r'RSA_OAEP'],
            'aes':   [r'AES\s*[\(\.]', r'AES\.new', r'aes[-_]?encrypt'],
            'ecdsa': [r'ECDSA', r'ECC\s*[\(\.]', r'SigningKey', r'ec\.generate'],
            'ecdh':  [r'ECDH', r'X25519', r'X448', r'key[-_]?exchange'],
            'dh':    [r'DiffieHellman', r'DH\s*[\(\.]', r'dh[-_]?key'],
            'sha':   [r'SHA[-_]?1', r'SHA[-_]?256', r'hashlib\.sha'],
            'md5':   [r'MD5', r'hashlib\.md5'],
            'dsa':   [r'DSA\s*[\(\.]', r'dsa[-_]?key', r'DSA\.generate'],
        }

        if crypto_type == 'all':
            patterns = [p for ps in crypto_patterns.values() for p in ps]
        else:
            patterns = crypto_patterns.get(crypto_type, [])

        if not patterns:
            return {'success': False, 'error': f'Unknown crypto type: {crypto_type}'}

        combined = '|'.join(f'({p})' for p in patterns)
        raw = self._search_code(combined, None, is_regex=True, case_sensitive=False)

        if raw['success']:
            categorized = {}
            for match in raw['result']['matches']:
                for ctype, pats in crypto_patterns.items():
                    if any(re.search(p, match['match'], re.I) for p in pats):
                        categorized.setdefault(ctype, []).append(match)
                        break

            return {
                'success': True,
                'result': {
                    'categorized_matches': categorized,
                    'summary': {k: len(v) for k, v in categorized.items()}
                }
            }
        return raw

    def _get_file_summary(self, path: str) -> dict:
        """Get structured summary of a file (classes, functions, imports)."""
        result = self._read_file(path)
        if not result['success']:
            return result

        content = result['result']['content']
        lines = content.split('\n')

        summary = {
            'path': path,
            'total_lines': len(lines),
            'classes': [],
            'functions': [],
            'imports': [],
        }

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('class '):
                name = stripped.split('(')[0].replace('class ', '').strip(':')
                summary['classes'].append({'name': name, 'line': i})
            elif stripped.startswith('def '):
                name = stripped.split('(')[0].replace('def ', '').strip()
                summary['functions'].append({'name': name, 'line': i})
            elif stripped.startswith(('import ', 'from ')):
                summary['imports'].append({'statement': stripped, 'line': i})

        return {'success': True, 'result': summary}


# --- Main ---
if __name__ == '__main__':
    import sys

    repo = sys.argv[1] if len(sys.argv) > 1 else '.'
    tools = RepositoryTools(repo)

    print(f"Repository: {repo}")
    print(f"Tools available: {len(tools.get_tool_definitions())}\n")

    # List files
    result = tools.execute_tool('list_files', {'path': '.', 'recursive': False})
    if result['success']:
        print(f"Root items: {result['result']['count']}")

    # Find crypto usage
    result = tools.execute_tool('find_crypto_usage', {'crypto_type': 'all'})
    if result['success']:
        summary = result['result'].get('summary', {})
        if summary:
            print(f"\nCrypto usage found:")
            for ctype, count in summary.items():
                print(f"  {ctype}: {count} matches")
        else:
            print("\nNo cryptographic patterns found.")
