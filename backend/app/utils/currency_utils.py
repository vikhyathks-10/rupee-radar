"""Currency and amount parsing utilities for Indian financial formats."""

import re
from typing import Optional


def parse_amount(amount_str: str, type_str: str = "") -> Optional[float]:
    """Parse an amount string into a signed float.
    
    Handles:
    - Indian comma format: "1,23,456.00"
    - Currency symbols: "₹1,234", "Rs. 1,234", "INR 1234"
    - Accounting notation: "(1,234)" → negative
    - Cr/Dr indicators: "1234 Cr" → positive, "1234 Dr" → negative
    - Parenthesized amounts: "(1234)" → negative
    
    Returns None if parsing fails.
    """
    if not amount_str or not amount_str.strip():
        return None

    s = amount_str.strip()

    # Determine sign
    is_negative = False

    # Accounting notation: parentheses mean negative
    if s.startswith("(") and s.endswith(")"):
        is_negative = True
        s = s[1:-1]

    # Strip currency symbols
    s = re.sub(r'[₹]|Rs\.|INR|INR\s', '', s, flags=re.IGNORECASE).strip()

    # Remove all commas (Indian grouping)
    s = s.replace(",", "")

    # Remove embedded spaces
    s = re.sub(r'\s+', '', s)

    # Strip Cr/Dr suffix
    cr_dr_match = re.search(r'\s*(Cr|Dr)\s*$', s, re.IGNORECASE)
    if cr_dr_match:
        indicator = cr_dr_match.group(1).upper()
        if indicator == "DR":
            is_negative = True
        # Remove the suffix
        s = s[:cr_dr_match.start()].strip()

    # Also check the separate type column
    if type_str:
        type_upper = type_str.strip().upper()
        if type_upper in ("DR", "DEBIT", "D"):
            is_negative = True
        elif type_upper in ("CR", "CREDIT", "C"):
            is_negative = False

    # Try to parse as float
    try:
        value = float(s)
    except ValueError:
        return None

    # Apply sign
    if is_negative:
        return -abs(value)
    else:
        return abs(value)
