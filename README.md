# into-farm

A repository in which I'll be getting into the FARM stack to become a fullstack developer.

---

## Content

- [Pyenv](#installing-and-managing-python-with-pyenv-on-macos)
  - [Prerequisites](#prerequisites)
  - [Installation](#pyenv-installation)
- [Poetry](#installing-and-managing-virtual-environments-with-poetry)
  - [Installation](#install-poetry)

---

## Installing and Managing Python with pyenv on macOS

### Prerequisites

Install Homebrew if you haven't already:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Pyenv installation

1. **Install pyenv:**

```bash
brew install pyenv
```

2. **Configure your shell:**

For **Zsh** (default on macOS):

```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
```

For **Bash**:

```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
```

3. **Restart your terminal** or run:

```bash
source ~/.zshrc  # or source ~/.bash_profile
```

### Basic Usage

#### Install Python versions

```bash
# List available Python versions
pyenv install --list

# Install a specific version
pyenv install 3.11.5

# Install the latest 3.12
pyenv install 3.12
```

#### Manage Python versions

```bash
# List installed versions
pyenv versions

# Set global Python version (system-wide)
pyenv global 3.11.5

# Set local Python version (for current directory)
pyenv local 3.12.0

# Set shell Python version (for current session)
pyenv shell 3.11.5
```

#### Verify installation

```bash
# Check active Python version
python --version

# Check which Python is being used
which python
```

### Common Commands

```bash
# Uninstall a Python version
pyenv uninstall 3.10.0

# Update pyenv
brew upgrade pyenv

# Rehash after installing packages with pip
pyenv rehash
```

### pyenv tips

- Use `.python-version` file in your project root to auto-activate specific Python versions
- Each Python version has its own isolated pip and packages
- Always run `pyenv rehash` after installing new packages globally

### Troubleshooting

If Python isn't switching versions:

1. Make sure shell configuration was added correctly
2. Restart your terminal
3. Check `echo $PATH` includes `.pyenv/shims`

---

### Installing and Managing Virtual Environments with Poetry

### Install poetry

**Install Poetry:**

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**Add to PATH:**

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Verify:**

```bash
poetry --version
```

### Configuration

```bash
# Create virtual environments inside project directory
poetry config virtualenvs.in-project true
```

### Quick Start

#### New project

```bash
poetry new my-project
cd my-project
```

#### Existing project

```bash
cd my-project
poetry init
```

### Managing Dependencies

```bash
# Add a package
poetry add requests

# Add dev dependency
poetry add --group dev pytest

# Remove package
poetry remove requests

# Install all dependencies
poetry install
```

### Using Virtual Environments

```bash
# Activate environment
poetry shell

# Run command without activating
poetry run python script.py

# Exit environment
exit
```

### Working with pyenv

```bash
# Set Python version for project
pyenv local 3.11.5

# Use it with Poetry
poetry env use python

# Verify
poetry env info
```

### Essential Commands

```bash
poetry install          # Install from poetry.lock
poetry update          # Update dependencies
poetry show            # List packages
poetry env list        # List environments
poetry env remove python  # Remove environment
```

### Important Files

- `pyproject.toml` - Dependencies and config
- `poetry.lock` - Locked versions (commit this!)
- `.python-version` - pyenv version (commit this!)

### poetry tips

- Always commit `poetry.lock`
- Use `poetry shell` for interactive work
- Use `poetry run` for scripts/commands
- Keep dev dependencies separate with `--group dev`