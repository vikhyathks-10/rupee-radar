"""AI categorization chain — sends uncategorized transactions to Groq for classification."""

import json
import logging

from app.ai.openai_client import GroqClient
from app.ai.prompts import CATEGORIZE_SYSTEM_PROMPT, CATEGORIZE_BATCH_USER_PROMPT

logger = logging.getLogger(__name__)


class CategorizeChain:
    """Chain that batches uncategorized transactions and sends them to Groq for categorization."""

    def __init__(self, client: GroqClient = None):
        self.client = client or GroqClient()
        self.batch_size = 20  # Max transactions per API call

    def categorize_batch(self, transactions: list[dict]) -> list[dict]:
        """Categorize a batch of transactions using Groq AI.
        
        Input: [{"description": str, "amount": float}]
        Output: [{"category": str, "confidence": float}]
        """
        results = []

        # Process in sub-batches to avoid exceeding token limits
        for i in range(0, len(transactions), self.batch_size):
            sub_batch = transactions[i:i + self.batch_size]
            batch_results = self._process_sub_batch(sub_batch)
            results.extend(batch_results)

        # If results length doesn't match transactions, fill missing with "Other"
        while len(results) < len(transactions):
            results.append({"category": "Other", "confidence": 0.3})

        return results

    def _process_sub_batch(self, transactions: list[dict]) -> list[dict]:
        """Process a sub-batch of transactions."""
        # Build the transaction list text
        txn_lines = []
        for j, txn in enumerate(transactions):
            desc = txn.get("description", "Unknown")
            amt = txn.get("amount", 0)
            txn_lines.append(f"{j+1}. Description: {desc}, Amount: {amt}")

        txn_text = "\n".join(txn_lines)

        user_prompt = CATEGORIZE_BATCH_USER_PROMPT.format(transactions=txn_text)

        messages = [
            {"role": "system", "content": CATEGORIZE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        response_text = self.client.chat_completion(messages, temperature=0.1, max_tokens=2000)

        if not response_text:
            # AI failed — return "Other" for all
            return [{"category": "Other", "confidence": 0.3} for _ in transactions]

        # Parse the JSON response
        try:
            parsed = json.loads(response_text)
            # Handle both array and dict responses
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict):
                # Sometimes the AI wraps the array in a dict key
                for key in ["results", "categories", "transactions", "data"]:
                    if key in parsed and isinstance(parsed[key], list):
                        return parsed[key]
                # Single transaction case
                return [parsed]
        except json.JSONDecodeError:
            logger.error(f"Failed to parse AI categorization response: {response_text[:200]}")

        # Fallback: return "Other" for all
        return [{"category": "Other", "confidence": 0.3} for _ in transactions]
