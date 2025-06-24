from enum import Enum

from fastapi import FastAPI, Query


class ShareMode(str, Enum):
    read_only = "read-only"
    interactive = "interactive"


app = FastAPI()


@app.get("/share/{notebook_id}")
def share_notebook(notebook_id: str, mode: ShareMode = Query(ShareMode.read_only)):
    """Return a shareable notebook link in the requested mode."""
    base_url = "https://example.com/notebooks"
    link = f"{base_url}/{notebook_id}?mode={mode.value}"
    return {"shareable_link": link}
