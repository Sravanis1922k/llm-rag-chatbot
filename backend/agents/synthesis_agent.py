"""Synthesis Agent — generates answer from retrieved chunks using LLM."""
import config, logging
logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """You are ARIA, an academic assistant. Answer the question using ONLY the context below.
If the answer is not in the context, say "I don't have enough information to answer that."
Always cite the source document name when referencing specific information.

Context:
{context}

Question: {question}

Answer:"""

class SynthesisAgent:
    def __init__(self):
        self.llm = self._load_llm()

    def _load_llm(self):
        if config.LLM_PROVIDER == "openai":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=config.OPENAI_LLM_MODEL, api_key=config.OPENAI_API_KEY)
        else:
            from langchain_community.llms import Ollama
            return Ollama(model=config.OLLAMA_LLM_MODEL)

    def synthesise(self, query: str, chunks: list[dict]) -> str:
        if not chunks:
            return "No relevant documents found. Please upload documents first."
        context = "\n\n".join([
            f"[Source: {c.get('source','unknown')}]\n{c.get('text','')}"
            for c in chunks
        ])
        prompt = PROMPT_TEMPLATE.format(context=context, question=query)
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return f"Error generating answer: {str(e)}"
