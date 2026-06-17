"""Retrieval Agent — semantic search + reranking."""
import logging
logger = logging.getLogger(__name__)

class RetrievalAgent:
    def __init__(self, retriever):
        self.retriever = retriever

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        results = self.retriever.search(query, top_k=top_k)
        logger.info(f"Retrieved {len(results)} chunks for query: '{query}'")
        return results
