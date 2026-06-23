"""Hybrid transaction categorizer — rule-based first pass + AI second pass."""

import json
import logging
import os
import re
from typing import Optional

from app.utils.text_utils import scrub_pii

logger = logging.getLogger(__name__)

VALID_CATEGORIES = [
    "Food", "Travel", "Shopping", "Bills", "EMI",
    "Subscriptions", "Salary", "Rent", "Investments", "Other",
]

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_category_keywords() -> dict:
    """Load the category keyword dictionary from JSON."""
    path = os.path.join(_DATA_DIR, "category_keywords.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class CategorizerService:
    """Hybrid categorizer: rule-based keywords → AI fallback."""

    def __init__(self, ai_chain=None):
        self.keywords_map = load_category_keywords()
        self.ai_chain = ai_chain  # Injected later; None means rule-only mode
        self._ai_cache = {}  # Cache AI results by normalized description

    def categorize(self, transactions: list[dict]) -> list[dict]:
        """Categorize a list of cleaned transactions using hybrid approach.
        
        Layer 1: Rule-based keyword/pattern matching (covers ~60-70%)
        Layer 2: AI categorization for remaining items (covers ~30-40%)
        """
        # First pass: rule-based
        for txn in transactions:
            category = self._rule_based_categorize(txn["description"], txn["original_description"])
            if category:
                txn["category"] = category
                txn["confidence"] = 1.0  # Rule-based = full confidence

        # Collect uncategorized transactions
        uncategorized = [txn for txn in transactions if txn["category"] == "Other"]

        # Second pass: AI (if available)
        if self.ai_chain and uncategorized:
            self._ai_categorize(uncategorized)

        return transactions

    def _rule_based_categorize(self, description: str, original_description: str) -> Optional[str]:
        """Try to categorize using keyword matching and regex patterns.
        
        Uses the original_description for matching (richer context),
        and the cleaned description as fallback.
        """
        search_text = original_description.upper()
        if not search_text:
            search_text = description.upper()

        # Check keywords and patterns for each category
        # Priority: longer/specific matches first (e.g., "AMAZON PRIME" before "AMAZON")
        best_match = None
        best_match_length = 0

        for category, rules in self.keywords_map.items():
            if category == "Other":
                continue

            # Check keyword matches
            for keyword in rules.get("keywords", []):
                kw_upper = keyword.upper()
                if kw_upper in search_text:
                    match_length = len(kw_upper)
                    # Longer match wins (e.g., "AMAZON PRIME" > "AMAZON")
                    if match_length > best_match_length:
                        best_match = category
                        best_match_length = match_length

            # Check regex pattern matches
            for pattern in rules.get("patterns", []):
                try:
                    if re.search(pattern, search_text):
                        # Pattern match is strong — use it
                        best_match = category
                        best_match_length = 999  # Pattern match overrides keyword
                        break
                except re.error:
                    logger.warning(f"Invalid regex pattern: {pattern}")

        return best_match

    def _ai_categorize(self, transactions: list[dict]) -> None:
        """Use AI (Groq) to categorize uncategorized transactions.
        
        Processes in batches. Caches results by normalized description.
        """
        batch = []
        for txn in transactions:
            # Check cache first
            normalized_desc = txn["description"].upper().strip()
            if normalized_desc in self._ai_cache:
                cached = self._ai_cache[normalized_desc]
                txn["category"] = cached["category"]
                txn["confidence"] = cached["confidence"]
                continue

            # Scrub PII before sending to AI
            scrubbed_desc = scrub_pii(txn["description"])
            batch.append({
                "description": scrubbed_desc,
                "amount": txn["amount"],
                "original_index": len(batch),  # Track position in batch
                "normalized_desc": normalized_desc,
            })

        if not batch:
            return

        # Send batch to AI
        try:
            results = self.ai_chain.categorize_batch(
                [{"description": b["description"], "amount": b["amount"]} for b in batch]
            )

            for i, result in enumerate(results):
                if i >= len(batch):
                    break

                normalized_desc = batch[i]["normalized_desc"]
                category = result.get("category", "Other")
                confidence = result.get("confidence", 0.5)

                # Validate category against allowed list
                if category not in VALID_CATEGORIES:
                    category = "Other"

                # Cross-validate: category should match amount sign
                # (Salary/Investments should typically be positive; EMI/Subscriptions negative)
                amount = batch[i]["amount"]
                category = self._validate_category_sign(category, amount)

                # Cache the result
                self._ai_cache[normalized_desc] = {"category": category, "confidence": confidence}

                # Update the transaction
                transactions[i]["category"] = category
                transactions[i]["confidence"] = confidence

        except Exception as e:
            logger.error(f"AI categorization failed: {e}. Falling back to 'Other' for remaining items.")

    def _validate_category_sign(self, category: str, amount: float) -> str:
        """Validate that a category makes sense given the transaction amount sign.
        
        EMI/Subscriptions/Rent/Bills/Food/Travel/Shopping → typically negative (debit)
        Salary → typically positive (credit)
        Investments → mixed (SIP is debit, dividend is credit)
        Other → no constraint
        """
        debit_categories = {"EMI", "Subscriptions", "Rent", "Bills", "Food", "Travel", "Shopping"}
        credit_categories = {"Salary"}

        if amount > 0 and category in debit_categories:
            # Debit category on a credit amount → likely misclassified
            return "Other"
        if amount < 0 and category in credit_categories:
            # Salary category on a debit amount → likely misclassified
            return "Other"

        return category
