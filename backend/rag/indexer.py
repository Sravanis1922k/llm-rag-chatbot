"""Indexer — stores document chunks in Qdrant."""
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
import config, uuid, logging
logger = logging.getLogger(__name__)

class Indexer:
    def __init__(self, embedder):
        self.embedder = embedder
        self.client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
        self._ensure_collection()

    def _ensure_collection(self):
        cols = [c.name for c in self.client.get_collections().collections]
        if config.QDRANT_COLLECTION not in cols:
            self.client.create_collection(
                config.QDRANT_COLLECTION,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE)
            )
            logger.info(f"Created Qdrant collection: {config.QDRANT_COLLECTION}")

    def index(self, chunks):
        texts = [c.page_content for c in chunks]
        vectors = self.embedder.embed(texts)
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vec,
                payload={"text": text, "source": chunk.metadata.get("source", "unknown")}
            )
            for text, vec, chunk in zip(texts, vectors, chunks)
        ]
        self.client.upsert(collection_name=config.QDRANT_COLLECTION, points=points)
        logger.info(f"Indexed {len(points)} chunks into Qdrant")
