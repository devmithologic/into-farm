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

---

## Notes from FastAPI Tutorial

Creating `app` folder is a common practice when developing a FastAPI application.


### Getting into Imagekit.io

This will be the API in which we can upload and manage all the image stuff
[ImageKit.io](https://imagekit.io/dashboard/)

From there is needed to create an account (it's free) and then go to developer options, from there we can get the values needed for our `.env` file such as our `PRIVATE_KEY`, `PUBLIC_KEY` and our `IMAGEKIT_URL`.


### The main file

We need to import uvicorn and with `uvicorn.run` we need to pass down the app argument constructed this way:

`app.app:app` -> `folder.file:function`
There is a folder `app/app.py` and within is a function called `app = FastAPI()`, so thats it.

```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.app:app", host="0.0.0.0", port=8000, reload=True)
```
---
# FastAPI Concepts

### Async
TODO: Introduce documentation and concepts.