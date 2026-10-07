from pathlib import Path
import modal

APP_NAME = "t5-text-summarizer"
MODEL_NAME = "Vansh-02/t5-text-summarizer"

app = modal.App(APP_NAME)


# Download the Hugging Face model while building the image,
# so it does not need to download 231 MB on every cold start.
def download_model():
    from huggingface_hub import snapshot_download

    snapshot_download(MODEL_NAME)


image = (
    modal.Image.debian_slim(python_version="3.13")
    .pip_install_from_requirements("requirements.txt")
    .run_function(download_model)
    .add_local_file("app.py", "/root/app.py")
    .add_local_dir("static", "/root/static")
    .add_local_dir("template", "/root/template")
)


@app.function(
    image=image,
    memory=2048,
    timeout=600,
)
@modal.asgi_app()
def web():
    import os

    # app.py expects ./static and ./template
    os.chdir("/root")

    from app import app as fastapi_app

    return fastapi_app