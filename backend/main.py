"""
ARIA — Academic Retrieval & Intelligence Assistant
FastAPI Backend — /ingest, /chat, /documents, /health
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import shutil, os, logging, time
from pathlib import Path

from agents.ingest_agent import IngestAgent
from agents.retrieval_agent import RetrievalAgent
from agents.synthesis_agent import SynthesisAgent
from rag.embedder import Embedder
from rag.indexer import Indexer
from rag.retriever import Retriever

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="ARIA — Academic RAG Assistant", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

embedder    = Embedder()
indexer     = Indexer(embedder)
retriever   = Retriever(embedder)
ingestor    = IngestAgent(indexer)
retrieval   = RetrievalAgent(retriever)
synthesiser = SynthesisAgent()

class ChatRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    latency_seconds: float
    chunks_retrieved: int

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}

@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    allowed = {".txt", ".pdf", ".md"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(400, f"File type {ext} not supported. Use: {allowed}")
    dest = UPLOAD_DIR / file.filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    try:
        n_chunks = ingestor.ingest(str(dest))
        return {"status": "indexed", "file": file.filename, "chunks": n_chunks}
    except Exception as e:
        raise HTTPException(500, f"Ingestion failed: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.query.strip():
        raise HTTPException(400, "Query cannot be empty")
    start = time.time()
    chunks = retrieval.retrieve(req.query, top_k=req.top_k)
    answer = synthesiser.synthesise(req.query, chunks)
    latency = round(time.time() - start, 3)
    sources = list({c["source"] for c in chunks if "source" in c})
    return ChatResponse(answer=answer, sources=sources, latency_seconds=latency, chunks_retrieved=len(chunks))

@app.get("/documents")
def list_documents():
    files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
    return {"documents": files, "count": len(files)}
