"""Transaction cleaner — normalizes dates, amounts, descriptions and deduplicates."""

import logging
from datetime import date

from app.utils.date_utils import parse_date
from app.utils.currency_utils import parse_amount
from app.utils.text_utils import clean_description

logger = logging.getLogger(__name__)


class CleanerService:
    """Clean and normalize raw transaction data."""

    def clean(self, raw_transactions: list[dict]) -> list[dict]:
        """Clean a list of raw transaction dicts.
        
        Input: [{date: str, description: str, amount: str, type: str}]
        Output: [{date: date_obj, description: str, original_description: str,
                  amount: float (signed), category: "Other"}]
        
        Steps:
        1. Parse dates into Python date objects
        2. Normalize amounts to signed floats (negative for debits)
        3. Clean descriptions (strip noise, normalize UPI/NEFT)
        4. Remove rows with missing critical fields
        5. Deduplicate exact same (date, amount, description)
        """
        cleaned = []
        seen = set()  # For deduplication

        for row in raw_transactions:
            # Parse date
            date_obj = parse_date(row.get("date", ""))
            if date_obj is None:
                logger.warning(f"Skipping row with unparseable date: {row.get('date', '')}")
                continue

            # Parse amount (signed)
            amount = parse_amount(row.get("amount", ""), row.get("type", ""))
            if amount is None:
                logger.warning(f"Skipping row with unparseable amount: {row.get('amount', '')}")
                continue

            # Clean description
            original_desc = row.get("description", "").strip()
            cleaned_desc = clean_description(original_desc)
            if not cleaned_desc:
                cleaned_desc = "Unknown Transaction"

            # Deduplication: skip if exact same (date, amount, original_desc)
            dedup_key = (date_obj, amount, original_desc.upper())
            if dedup_key in seen:
                logger.debug(f"Deduplicating: {original_desc} on {date_obj}")
                continue
            seen.add(dedup_key)

            cleaned.append({
                "date": date_obj,
                "description": cleaned_desc,
                "original_description": original_desc,
                "amount": amount,
                "category": "Other",  # Default; will be updated by categorizer
                "is_recurring": False,
                "confidence": None,
            })

        return cleaned
