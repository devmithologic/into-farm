# Followed Steps
---
## Environment Setup

### Pyenv Setup

I decided to work with Python3.12.10 version.

```bash
pyenv install 3.12.10

# Within the project folder I like to set the local version.
pyenv local 3.12.10
```


### Poetry Setup

```bash
poetry init
```

This will guide you to a 

#### Install poetry dependencies

```bash
poetry add fastapi
poetry add python-dotenv
poetry add imagekitio
poetry add 'fastapi-users[sqlalchemy]'
poetry add 'uvicorn[standard]'
poetry add aiosqlite
```