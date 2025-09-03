# GKI Kernel Builder

[![codecov](https://codecov.io/gh/bachnxuan/gki_kernel_builder/graph/badge.svg?token=EYKHK1OOC4)](https://codecov.io/gh/bachnxuan/gki_kernel_builder) [![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?logo=telegram&logoColor=white)](https://t.me/xaga_kernel)

Effortlessly building Android Generic Kernel Image (GKI).

---

## Table of Contents

- [Requirements](#requirements)
- [Setup Kernel Builder](#setup-kernel-builder)
- [Build the kernel](#build-the-kernel)
  - [Quick Start](#quick-start)
  - [Setup Environment](#setup-environment)
  - [CLI Structure](#cli-structure)
  - [Example Commands](#example-commands)
- [GitHub Workflows](#github-workflows)
- [Configuration](#configuration)
- [License](#license)

---

## Requirements

- Linux
- Python 3.12

### System packages:

* Debian-based

  ```bash
  sudo apt update
  sudo apt install --no-install-recommends \
    bc bison ccache curl flex git tar wget aria2 jq make
  ```

* Fedora

  ```bash
  sudo dnf install bc bison ccache curl flex git tar wget aria2 jq make
  ```

### Install uv (python package manager):

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  uv --version
  ```

### Ensure Python 3.12 installed

  >[!NOTE]
  > If your distro already ships Python 3.12, you can skip this step.

  ```bash
  uv python install 3.12
  uv run -p 3.12 -- python -V    # should print 3.12.x
  ```

---

## Setup Kernel Builder

1. **Clone the repository**:

   ```bash
   git clone --recurse-submodule https://github.com/bachnxuan/gki_kernel_builder.git
   cd gki_kernel_builder
   ```

2. **Set up venv**:

   ```bash
   uv sync --frozen --no-install-project
   source .venv/bin/activate
   ```

   Once you are finished working with the project, disable the virtual environment (venv) via `deactivate`.

## Build the kernel

Builds are performed via the custom wrapper script `cli.sh`

### Setup Environment

> [!NOTE]
> PAT scopes (read and write): `workflow`, `content`

1. Rename `.env.template` to `.env`
2. Fill in the GH_TOKEN in `.env`

### Quick Start

To build your kernel with default configuration:

```bash
./cli.sh build
```

### CLI Structure

The CLI consists of the following commands:

- **build** - Configure and compile the kernel

- **clean** - Clean up build artifacts

View all available options:

```bash
./cli.sh --help
```

### Example Commands

Build KernelSU NEXT with SUSFS (no LXC):

```bash
./cli.sh build -k NEXT -s
```

Build SukiSU with LXC without SUSFS:

```bash
./cli.sh build --ksu SUKI --no-susfs --lxc
```

---

## GitHub Workflows

1. **Fork** this repo to your GitHub account.

2. **Add secret** `GH_TOKEN`

   - PAT scopes (read and write): `workflow`, `content`
   - Add PAT access to your release and kernel builder repo
   - Repo → Settings → Secrets → Actions → **New secret**.

3. **Optional Telegram secrets**

> [!NOTE]
> Add the below Telegram secrets below when you want to notify completed build on Telegram.
> The Telegram notify feature can be config via `NOTIFY` on workflows_dispatch and workflows_call input.

- `TG_BOT_TOKEN` – Telegram Bot Token
- `TG_CHAT_ID` – Telegram Chat ID

---

## Configuration

> [!WARNING]
> If you build a GKI kernel for devices other than xaga (ESK Kernel), set LXC to false or remove the LXC function entirely.

Customize your build by:

- `config/config.py` – Contains kernel configuration settings.
- `config/manifest.py` – Specifies repository sources and branches.
- `kernel_builder.py` – The main script responsible for orchestrating the build.

> [!NOTE]
> See the dedicated guide for more information: [Kernel Builder Configuration guide](https://github.com/ESK-Project/gki_kernel_builder/tree/master/kernel_builder/config)

---

## License

This project is distributed under the [GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.en.html). See `LICENSE` for details.
