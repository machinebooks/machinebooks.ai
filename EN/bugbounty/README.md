# Book 10 — The Bug Bounty Hunter and the Machine

> **This book is currently in editing and will be available soon.** The companion code below is a preview of the patterns and tools that will accompany the final publication.

**Companion code for *Bug Bounty Hunter and the Machine: Security Research with AI — From Docker Lab to Bounty Report*.**

This folder contains the Docker lab, exploit PoCs, analysis scripts, and report templates referenced throughout the book.

## Directory structure

```
bugbounty/
├── lab/                  # Docker environment and setup
│   ├── Dockerfile        # radare2, Capstone, boofuzz, pefile, impacket, yara
│   └── docker-compose.yml
├── exploits/             # PoC code in C and Python
│   ├── dll-hijacking/
│   ├── asar-tampering/
│   ├── ioctl-fuzzing/
│   └── prompt-injection/
├── analysis/             # Static and dynamic analysis scripts
│   ├── pe-analysis/
│   ├── dacl-audit/
│   ├── fuse-enum/
│   └── import-mapping/
├── reports/              # Report templates by platform
│   ├── hackerone/
│   ├── bugcrowd/
│   └── zdi/
└── agents/               # Claude agent patterns for security research
```

## Chapter-to-file mapping

| Chapter | Title | Files |
|---------|-------|-------|
| 1 | The first vulnerability an agent found | `agents/agent_vuln_discovery.py` |
| 2 | The augmented hunter's stack | `lab/Dockerfile`, `lab/docker-compose.yml` |
| 3 | Ethics, legality, and responsible disclosure | `reports/disclosure_template.md` |
| 4 | Electron: the attack surface nobody audits | `analysis/fuse-enum/electron_fuse_check.py` |
| 5 | ASAR tampering: from app to RCE | `exploits/asar-tampering/asar_extract_inject.py` |
| 6 | DLL sideloading: the classic that still works | `exploits/dll-hijacking/proxy_dll.c`, `exploits/dll-hijacking/dll_hijack_check.py` |
| 7 | Code signing and bypasses | `analysis/import-mapping/wintrust_analysis.py` |
| 8 | Driver analysis with AI | `analysis/pe-analysis/pe_analyzer.py`, `analysis/pe-analysis/ioctl_scanner.py` |
| 9 | IOCTL fuzzing assisted by Claude | `exploits/ioctl-fuzzing/ioctl_fuzzer.py`, `exploits/ioctl-fuzzing/boofuzz_smb.py` |
| 10 | Memory corruption in drivers | `exploits/ioctl-fuzzing/memory_corruption_pocs.c` |
| 11 | From vulnerable driver to kernel read/write | `exploits/ioctl-fuzzing/kernel_rw_poc.c` |
| 12 | Prompt injection to RCE: the new OWASP #1 | `exploits/prompt-injection/copilot_injection_poc.md` |
| 13 | VM escape and RPC abuse | `exploits/prompt-injection/rpc_enumeration.py` |
| 14 | Extension tampering and code integrity | `analysis/fuse-enum/integrity_check.py` |
| 15 | Cookie theft, token theft, and persistence | `analysis/dacl-audit/credential_audit.py` |
| 16 | Reconnaissance and surface mapping with AI | `analysis/dacl-audit/dacl_scanner.py`, `analysis/import-mapping/surface_mapper.py` |
| 17 | Writing the PoC that proves impact | `exploits/dll-hijacking/proxy_dll_template.c` |
| 18 | The report that pays: bug bounty report anatomy | `reports/hackerone/template.md`, `reports/bugcrowd/template.md`, `reports/zdi/template.md` |
| 19 | Triage, negotiation, and follow-up | `reports/follow_up_template.md` |
| 20–25 | Real-world case studies (6 cases) | *Code will be published after vendor coordination* |
| 26 | From hobby to profession: the economics of bug bounty | `agents/agent_roi_tracker.py` |
| 27 | The future: offensive AI, defensive AI, and the hunter in between | `agents/agent_autonomous_hunter.py` |

## Important: Responsible disclosure

All vulnerability research described in this book and this repository was conducted under authorized bug bounty programs or responsible disclosure policies. The exploit code provided here is for **educational and authorized testing purposes only**.

- **Never** use these tools against systems without explicit written authorization.
- **Always** follow the scope and rules of the bug bounty program you are participating in.
- **Report** vulnerabilities through proper channels before any public disclosure.
- Vendor names in PoC filenames are used for educational context only; all issues were reported to the respective vendors through their official security channels.

## Requirements

- Docker (for the analysis lab)
- Python 3.11+
- A C compiler (MSVC or MinGW for Windows PoCs)
- Claude Code or Claude API access (for agent-assisted workflows)

## License

MIT — See [LICENSE](../LICENSE) for details.
