import os
from typing import List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss


class RAGPipeline:
    """Simple pipeline for file ingestion, indexing with FAISS and retrieval."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", chunk_size: int = 500, chunk_overlap: int = 50):
        self.model = SentenceTransformer(model_name)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.index = None
        self.chunks: List[str] = []

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk = words[i:i + self.chunk_size]
            chunks.append(" ".join(chunk))
        return chunks

    def ingest_files(self, paths: List[str]):
        """Read files, chunk text and build FAISS index."""
        all_chunks = []
        for path in paths:
            if not os.path.exists(path):
                continue
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            chunks = self._chunk_text(text)
            all_chunks.extend(chunks)
        if not all_chunks:
            raise ValueError("No text data found in provided paths")
        self.chunks = all_chunks
        embeddings = self.model.encode(all_chunks, show_progress_bar=False)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(np.array(embeddings).astype("float32"))

    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[float, str]]:
        """Retrieve relevant chunks for a query."""
        if self.index is None:
            raise ValueError("Index has not been built. Call ingest_files first.")
        query_vec = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_vec).astype("float32"), top_k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.chunks):
                results.append((float(dist), self.chunks[idx]))
        return results

    def build_prompt(self, query: str, top_k: int = 5) -> str:
        """Construct a prompt for the language model using retrieved chunks."""
        retrieved = self.retrieve(query, top_k=top_k)
        context = "\n---\n".join(chunk for _, chunk in retrieved)
        prompt = (
            f"Answer the following question using only the context provided.\n"
            f"\nContext:\n{context}\n\nQuestion: {query}\nAnswer:")
        return prompt
