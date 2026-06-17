"""Embedder — wraps Ollama or OpenAI embeddings."""
import config

class Embedder:
    def __init__(self):
        self.model = self._load()

    def _load(self):
        if config.EMBEDDING_PROVIDER == "openai":
            from langchain_openai import OpenAIEmbeddings
            return OpenAIEmbeddings(model=config.OPENAI_EMBED_MODEL, api_key=config.OPENAI_API_KEY)
        else:
            from langchain_community.embeddings import OllamaEmbeddings
            return OllamaEmbeddings(model=config.OLLAMA_EMBED_MODEL)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self.model.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        return self.model.embed_query(text)
