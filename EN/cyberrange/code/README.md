# Cyber Range — Companion Code

**Companion code for "The Cyber Range and the Machine"**
(El Cyber Range y la Máquina)

This is **starter scaffold code**, not a production-ready platform. The book is the guide — this code is the starting point for readers who want to build their own Cyber Range.

## Directory Structure

```
code/
├── .env.example                          # All environment variables documented
├── docker-compose.yml                    # 4 services: frontend, backend, MySQL, Redis (Ch. 25)
├── backend/
│   ├── main.py                           # FastAPI app with routers, CORS, WebSocket (Ch. 9)
│   ├── auth.py                           # JWT + RBAC with 6 roles, account lockout (Ch. 24)
│   ├── models.py                         # Core SQLAlchemy models (~15 essential) (Ch. 11)
│   ├── services/
│   │   ├── proxmox_service.py            # Proxmox VE wrapper: clone, start, VNC (Ch. 10)
│   │   ├── flag_service.py               # Dynamic CTF flag generation + validation (Ch. 12)
│   │   ├── scenario_generator.py         # Claude Agent SDK scenario generation (Ch. 17)
│   │   ├── coaching_service.py           # AI coaching: hints, stall detection (Ch. 18)
│   │   └── red_team_agent.py             # Red team AI agent with guardrails (Ch. 19)
│   └── routers/
│       ├── gaming.py                     # CTF endpoints: submit flag, leaderboard (Ch. 12)
│       └── workzones.py                  # Workzone CRUD: create, VLAN, TTL (Ch. 8)
├── playbooks/
│   ├── setup-ubuntu-ssh-vuln.yml         # Ansible: vulnerable Ubuntu VM (Ch. 13)
│   └── setup-windows-smb-vuln.yml        # Ansible: vulnerable Windows VM (Ch. 13)
└── tests/
    ├── test_flag_service.py              # Flag generation/validation tests
    └── test_network_isolation.py         # Network isolation verification
```

## Quick Start

```bash
# 1. Copy environment variables
cp .env.example .env
# Edit .env with your actual API keys, Proxmox credentials, etc.

# 2. Start infrastructure
docker compose up -d

# 3. Install Python dependencies
cd backend
pip install -r requirements.txt  # (create your own based on imports)

# 4. Run the API
uvicorn main:app --reload --port 8000

# 5. Run tests
cd ../tests
pytest -v
```

## Chapter Map

| Chapter | Topic | Files |
|---------|-------|-------|
| Ch. 8   | Workzones & network isolation | `routers/workzones.py` |
| Ch. 9   | FastAPI backend architecture | `backend/main.py` |
| Ch. 10  | Proxmox integration | `services/proxmox_service.py` |
| Ch. 11  | Database design | `backend/models.py` |
| Ch. 12  | CTF & flag mechanics | `services/flag_service.py`, `routers/gaming.py` |
| Ch. 13  | Scenario automation | `playbooks/*.yml` |
| Ch. 17  | AI scenario generation | `services/scenario_generator.py` |
| Ch. 18  | AI coaching | `services/coaching_service.py` |
| Ch. 19  | Red team AI agent | `services/red_team_agent.py` |
| Ch. 24  | Security & authentication | `backend/auth.py` |
| Ch. 25  | Containerized deployment | `docker-compose.yml` |

## Important

- All API keys use placeholders (`<YOUR_API_KEY>`) — replace before running
- Security patterns follow book recommendations (bcrypt, hmac.compare_digest, etc.)
- This is educational code — review and harden before any real deployment
- Proxmox integration requires a real Proxmox VE server with API tokens configured

## License

MIT — See root repository for details.
