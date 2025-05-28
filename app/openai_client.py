import os
from openai import AzureOpenAI
from typing import List, Dict
from dotenv import load_dotenv
from logger import init_logger

logger = init_logger(name="chatbot.openai_client", level="DEBUG", filename="openai_client.log")


load_dotenv()

class AzureOpenAIClient:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        )
        self.chat_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        self.embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING")

    # ── Chat Completion ────────────────────────────────────────────────
    def chat(self, messages: List[Dict], temperature: float = 0.2) -> str:
        resp = self.client.chat.completions.create(
            model=self.chat_deployment,
            messages=messages,
            temperature=temperature,
            max_tokens=512,  # Limit response length
        )
        logger.info("LLM response: %s", resp.choices[0].message.content)
        # log.info("LLM tokens prompt=%s  completion=%s",
        #     resp.usage.prompt_tokens, resp.usage.completion_tokens)
        return resp.choices[0].message.content
    
    # ── Embeddings ─────────────────────────────────────────────────────
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Returns list of embedding vectors (length 1536 for ada‑002)."""
        resp = self.client.embeddings.create(
            model=self.embedding_deployment,
            input=texts,
        )
        return [d.embedding for d in resp.data]