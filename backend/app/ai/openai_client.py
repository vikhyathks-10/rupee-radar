"""Groq AI client — uses the OpenAI-compatible SDK to interact with Groq API."""

import logging
from typing import Optional

from openai import OpenAI

from app.config import settings

logger = logging.getLogger(__name__)


class GroqClient:
    """Wrapper around the OpenAI SDK configured for Groq's API endpoint."""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url,
        )
        self.model = settings.groq_model

    def chat_completion(
        self,
        messages: list[dict],
        temperature: float = 0.1,
        max_tokens: int = 2000,
    ) -> Optional[str]:
        """Send a chat completion request to Groq.
        
        Returns the assistant's response text, or None on failure.
        """
        if not settings.groq_api_key:
            logger.warning("No Groq API key configured — AI features disabled")
            return None

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            return None
