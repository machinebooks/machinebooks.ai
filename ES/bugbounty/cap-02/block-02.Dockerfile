# Extraído de: LibroBugBounty/cap-02-stack-hunter.md
FROM python:3.11-slim-bookworm

LABEL maintainer="security-lab"
LABEL description="Windows driver reversing & SMB fuzzing lab"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
