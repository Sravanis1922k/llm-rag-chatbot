"""Retriever — semantic search from Qdrant."""
from qdrant_client import QdrantClient
import config, logging
logger = logging.getLogger(__name__)

class Retriever:
    def __init__(self, embedder):
        self.embedder = embedder
        self.client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)

    def search(self, query: str, top_k: int = None) -> list[dict]:
        k = top_k or config.TOP_K
        vector = self.embedder.embed_query(query)
        results = self.client.search(
            collection_name=config.QDRANT_COLLECTION,
            query_vector=vector,
            limit=k,
            with_payload=True
        )
        return [
            {"text": r.payload.get("text",""), "source": r.payload.get("source","unknown"), "score": r.score}
            for r in results
        ]
