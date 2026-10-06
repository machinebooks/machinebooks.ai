# Book 10 — The Bug Bounty Hunter and the Machine

> **This book is currently in editing and will be available soon.** The companion code below is a preview of the patterns and tools that will accompany the final publication.

**Companion code for *Bug Bounty Hunter and the Machine: Security Research with AI — From Docker Lab to Bounty Report*.**

**Available in this folder:** this README only. The paths below describe planned companion material and are not download links or files currently supplied. The Spanish extraction is available separately in [ES/bugbounty](../../ES/bugbounty/), with chapter numbering from an earlier source snapshot.

## Planned directory structure — not currently supplied

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

## Planned chapter-to-file mapping — earlier outline

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

The outline above predates the current manuscript: economics and future are now chapters 35 and 36; the Spanish extraction headers still use 28 and 29 for those topics. Reconcile the complete map before announcing new companion availability. No files or private application source are added by this README update.

## Important: Responsible disclosure

Use any companion security-research material only within systems, programmes, and disclosure arrangements for which you have explicit authorization. This is a requirement for use, not independent confirmation of the authorization or disclosure history of every case in the book. No exploit files are currently supplied in this English folder.

- **Never** use these tools against systems without explicit written authorization.
- **Always** follow the scope and rules of the bug bounty program you are participating in.
- **Report** vulnerabilities through proper channels before any public disclosure.
- Before publishing case material or PoCs, verify authorization, disclosure status, and the vendor coordination applicable to that specific case. A vendor name or filename is not evidence that this process is complete.

## Requirements

- Docker (for the analysis lab)
- Python 3.11+
- A C compiler (MSVC or MinGW for Windows PoCs)
- Claude Code or Claude API access (for agent-assisted workflows)

## License

MIT — See [LICENSE](../../LICENSE) for details.

## Scope of the published material

A file being present does not establish execution, complete coverage, or synchronization with the edition you are reading. ES contains extracted code; EN may contain a different selection or exercises. Named providers and clients identify concrete cases; alternatives need separate capability, permission, privacy, quality, and cost checks.

See [LICENSE](../../LICENSE) and [LICENSING.md](../../LICENSING.md) for the boundaries of companion code, editorial text, and production tooling.

The reference application is private; this folder does not offer its source, a public download, or a current or future Community edition. Published didactic fragments and tests remain authorized under their existing MIT terms and do not constitute the product core.
