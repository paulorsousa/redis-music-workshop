# Prerequisites

Before starting, make sure the following tools are installed on your machine.

## Docker & Docker Compose

Docker is used to run all workshop services (Redis, PostgreSQL, API, and Frontend) in containers.

- **Docker Desktop** (includes Docker Engine + Docker Compose):
  - [Install Docker Desktop on Mac](https://docs.docker.com/desktop/setup/install/mac-install/)
  - [Install Docker Desktop on Linux](https://docs.docker.com/desktop/setup/install/linux/)

- **Docker Engine only** (Linux / WSL — if not using Docker Desktop):
  - [Install Docker Engine](https://docs.docker.com/engine/install/)
  - [Post-installation steps (manage Docker as a non-root user)](https://docs.docker.com/engine/install/linux-postinstall/)

- **Docker Compose** (standalone — only needed if Docker Compose is not bundled with your Docker installation):
  - [Install Docker Compose plugin](https://docs.docker.com/compose/install/)

Verify your installation:

```bash
docker --version            # e.g. Docker version 28.x
docker compose version      # e.g. Docker Compose version v2.x
```

## Python 3

Python 3 is required to run the `./workshop` CLI tool (it uses only the standard library — no pip packages needed).

- [Download Python 3 (official)](https://www.python.org/downloads/)
- **Mac** (via Homebrew): `brew install python`
- **Ubuntu / Debian / WSL**: `sudo apt install python3`
- **Fedora**: `sudo dnf install python3`

Verify your installation:

```bash
python3 --version           # e.g. Python 3.13.x
```
