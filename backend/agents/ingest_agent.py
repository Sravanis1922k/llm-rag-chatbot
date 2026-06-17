"""Ingest Agent — loads, chunks, and indexes documents."""
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path
import config, logging

logger = logging.getLogger(__name__)

class IngestAgent:
    def __init__(self, indexer):
        self.indexer = indexer
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )

    def ingest(self, filepath: str) -> int:
        ext = Path(filepath).suffix.lower()
        loaders = {".txt": TextLoader, ".pdf": PyPDFLoader, ".md": UnstructuredMarkdownLoader}
        if ext not in loaders:
            raise ValueError(f"Unsupported file type: {ext}")
        loader = loaders[ext](filepath)
        docs = loader.load()
        chunks = self.splitter.split_documents(docs)
        for chunk in chunks:
            chunk.metadata["source"] = Path(filepath).name
        self.indexer.index(chunks)
        logger.info(f"Ingested {filepath} → {len(chunks)} chunks")
        return len(chunks)
