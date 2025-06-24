from enum import Enum
from typing import List

from fastapi import FastAPI, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.rag_pipeline import RAGPipeline


class ShareMode(str, Enum):
    read_only = "read-only"
    interactive = "interactive"


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = RAGPipeline()

app.mount("/", StaticFiles(directory="frontend", html=True), name="static")


@app.get("/share/{notebook_id}")
def share_notebook(notebook_id: str, mode: ShareMode = Query(ShareMode.read_only)):
    """Return a shareable notebook link in the requested mode."""
    base_url = "https://example.com/notebooks"
    link = f"{base_url}/{notebook_id}?mode={mode.value}"
    return {"shareable_link": link}


@app.post("/ingest")
async def ingest(files: List[UploadFile] = File(...)):
    """Ingest uploaded text files into the retrieval pipeline."""
    paths = []
    for f in files:
        data = await f.read()
        path = f"/tmp/{f.filename}"
        with open(path, "wb") as out:
            out.write(data)
        paths.append(path)
    pipeline.ingest_files(paths)
    return {"status": "ingested", "count": len(paths)}


@app.get("/query")
def query(q: str):
    """Return retrieved context for the query."""
    prompt = pipeline.build_prompt(q)
    return {"prompt": prompt}
