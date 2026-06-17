"""Central config — reads from .env"""
import os
from dotenv import load_dotenv
load_dotenv()

LLM_PROVIDER        = os.getenv("LLM_PROVIDER", "ollama")          # ollama | openai
EMBEDDING_PROVIDER  = os.getenv("EMBEDDING_PROVIDER", "ollama")     # ollama | openai
OLLAMA_LLM_MODEL    = os.getenv("OLLAMA_LLM_MODEL", "llama3.2")
OLLAMA_EMBED_MODEL  = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
OPENAI_API_KEY      = os.getenv("OPENAI_API_KEY", "")
OPENAI_LLM_MODEL    = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
OPENAI_EMBED_MODEL  = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
QDRANT_HOST         = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT         = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_COLLECTION   = os.getenv("QDRANT_COLLECTION", "aria_docs")
CHUNK_SIZE          = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP       = int(os.getenv("CHUNK_OVERLAP", 50))
TOP_K               = int(os.getenv("TOP_K", 5))
RERANK_TOP_N        = int(os.getenv("RERANK_TOP_N", 3))
