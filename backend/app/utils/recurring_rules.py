"""Recurring merchant name matching rules."""

import json
import os
from typing import Optional


_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_recurring_merchants() -> list[dict]:
    """Load the recurring merchants dictionary from JSON."""
    path = os.path.join(_DATA_DIR, "recurring_merchants.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("recurring_merchants", [])


def match_known_recurring(merchant_name: str) -> Optional[dict]:
    """Check if a normalized merchant name matches a known recurring merchant.
    
    Returns the merchant dict if matched, None otherwise.
    """
    merchants = load_recurring_merchants()
    name_upper = merchant_name.upper()

    for merchant in merchants:
        for alias in merchant.get("aliases", []):
            if alias.upper() in name_upper or name_upper in alias.upper():
                return merchant

    return None
