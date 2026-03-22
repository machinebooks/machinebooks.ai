"""
PQC-Day and the Machine — Chapter 12
Pattern: CodeAnalysisAgent — autonomous cryptographic analysis with tool-calling loop

This is a didactic example from the book, not production code.
See chapter 12 for full context and explanation.

Requires: pip install anthropic
"""

import json
import os
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    import anthropic
except ImportError:
    anthropic = None


class CodeAnalysisAgent:
    """Autonomous cryptographic analysis agent with tool-calling loop."""

    MAX_ITERATIONS = 15  # Maximum iteration budget

    def __init__(self, repo_path: str, api_key: str = None):
        from tools import RepositoryTools

        self.repo_path = repo_path
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.tools = RepositoryTools(repo_path)
        self.tool_definitions = self._convert_tools_to_anthropic()
        self.actions_log = []

    def _convert_tools_to_anthropic(self) -> list:
        """Convert OpenAI-format tools to Anthropic format."""
        openai_tools = self.tools.get_tool_definitions()
        return [{
            'name': t['function']['name'],
            'description': t['function']['description'],
            'input_schema': t['function']['parameters']
        } for t in openai_tools]

    def _build_initial_messages(self, user_message: str,
                                 history: list) -> list:
        """Build initial context with PQC domain knowledge."""
        system_prompt = f"""You are an expert agent in cryptographic security and
post-quantum vulnerability (PQC) code analysis.

CONTEXT:
- You are analyzing the repository at: {self.repo_path}

PQC KNOWLEDGE:
- Algorithms VULNERABLE to quantum computing (Shor):
  RSA, DSA, ECDSA, ECDH, DH (require full migration)
- Algorithms WEAKENED by Grover:
  AES-128 (insufficient), SHA-256 (maintains acceptable security)
- PQC SAFE algorithms (migration target):
  ML-KEM (Kyber), ML-DSA (Dilithium), SLH-DSA (SPHINCS+), FN-DSA (Falcon)

WORKFLOW:
1. Explore the structure with list_files
2. Identify relevant files
3. Use find_crypto_usage for quick inventory
4. Read and analyze important files
5. Provide analysis with PQC migration recommendations

Always respond in English."""

        messages = [{'role': 'user', 'content': user_message}]

        # Add history (last 10 messages to maintain context)
        if history:
            for h in history[-10:]:
                messages.insert(0, {'role': h['role'], 'content': h['content']})

        return system_prompt, messages

    def run(self, user_message: str, history: list = None):
        """Main agent loop. Generates events for streaming.

        Events:
        - {'type': 'thinking',    'content': '...'}
        - {'type': 'tool_call',   'tool': 'list_files', 'args': {...}}
        - {'type': 'tool_result', 'tool': 'list_files', 'result': {...}}
        - {'type': 'response',    'content': '...', 'iterations': N}
        - {'type': 'error',       'content': '...'}
        """
        if not anthropic:
            yield {'type': 'error', 'content': 'anthropic package not installed'}
            return

        client = anthropic.Anthropic(api_key=self.api_key)
        system_prompt, messages = self._build_initial_messages(
            user_message, history or []
        )

        yield {'type': 'thinking', 'content': 'Analyzing your request...'}

        iteration = 0
        while iteration < self.MAX_ITERATIONS:
            iteration += 1

            # 1. Call model with available tools
            response = client.messages.create(
                model='claude-sonnet-4-6',
                max_tokens=4096,
                system=system_prompt,
                messages=messages,
                tools=self.tool_definitions,
                tool_choice={'type': 'auto'}
            )

            # 2. Process response content
            text_content = ""
            tool_calls = []

            for block in response.content:
                if block.type == 'text':
                    text_content += block.text
                elif block.type == 'tool_use':
                    tool_calls.append({
                        'id': block.id,
                        'name': block.name,
                        'arguments': block.input
                    })

            if tool_calls:
                # 3. Execute each tool and accumulate results
                messages.append({
                    'role': 'assistant',
                    'content': response.content
                })

                tool_results = []
                for tc in tool_calls:
                    tool_name = tc['name']
                    tool_args = tc['arguments']

                    yield {'type': 'tool_call', 'tool': tool_name, 'args': tool_args}

                    result = self.tools.execute_tool(tool_name, tool_args)
                    self.actions_log.append({
                        'tool': tool_name, 'args': tool_args, 'result': result
                    })

                    yield {
                        'type': 'tool_result', 'tool': tool_name,
                        'result': result, 'success': result.get('success', False)
                    }

                    tool_results.append({
                        'type': 'tool_result',
                        'tool_use_id': tc['id'],
                        'content': json.dumps(result, ensure_ascii=False)[:4000]
                    })

                # 4. Add results to context for next iteration
                messages.append({
                    'role': 'user',
                    'content': tool_results
                })
            else:
                # No tool_calls -> final agent response
                yield {
                    'type': 'response',
                    'content': text_content,
                    'iterations': iteration,
                    'actions': self.actions_log
                }
                return

        # Budget exhausted
        yield {
            'type': 'response',
            'content': 'Iteration limit reached. Partial result.',
            'iterations': iteration, 'truncated': True
        }

    def run_sync(self, user_message: str, history: list = None) -> dict:
        """Synchronous version for Celery tasks."""
        last_event = None
        for event in self.run(user_message, history):
            last_event = event
            if event['type'] in ('tool_call', 'tool_result'):
                logger.info(f"Agent: {event['type']} — {event.get('tool', '')}")
        return last_event or {'type': 'error', 'content': 'No result'}


# --- Main ---
if __name__ == '__main__':
    import sys

    repo = sys.argv[1] if len(sys.argv) > 1 else '.'
    query = sys.argv[2] if len(sys.argv) > 2 else \
        "Analyze the cryptographic posture of this repository"

    if not os.getenv('ANTHROPIC_API_KEY'):
        print("Set ANTHROPIC_API_KEY environment variable to run this agent.")
        sys.exit(1)

    print(f"Repository: {repo}")
    print(f"Query: {query}")
    print(f"{'='*60}\n")

    agent = CodeAnalysisAgent(repo)

    for event in agent.run(query):
        if event['type'] == 'thinking':
            print(f"[THINKING] {event['content']}")
        elif event['type'] == 'tool_call':
            print(f"[TOOL] {event['tool']}({json.dumps(event['args'])})")
        elif event['type'] == 'tool_result':
            status = 'OK' if event['success'] else 'FAIL'
            print(f"[RESULT] {event['tool']} -> {status}")
        elif event['type'] == 'response':
            print(f"\n{'='*60}")
            print(f"[RESPONSE] (iterations: {event['iterations']})")
            print(event['content'])
        elif event['type'] == 'error':
            print(f"[ERROR] {event['content']}")
