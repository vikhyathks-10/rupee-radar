"""Text cleaning and PII scrubbing utilities for transaction descriptions."""

import re


# PII patterns to scrub before sending to AI
PII_PATTERNS = [
    (re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b'), 'CARD_REF'),      # 16-digit card numbers
    (re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b'), 'AADHAAR_REF'),            # 12-digit Aadhaar
    (re.compile(r'\b[A-Z]{5}\d{4}[A-Z]\b'), 'PAN_REF'),                   # PAN number
    (re.compile(r'\b\d{10}\b'), 'PHONE_REF'),                              # 10-digit phone
    (re.compile(r'\b[\w.+-]+@[\w.-]+\.\w+\b'), 'EMAIL_REF'),              # Email
    (re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{3,4}\b'), 'ACCT_REF'),  # Account numbers
]


def clean_description(desc: str) -> str:
    """Clean a raw bank transaction description.
    
    - Strip extra whitespace
    - Remove trailing reference numbers
    - Normalize UPI format
    """
    if not desc:
        return ""

    s = desc.strip()

    # Remove extra whitespace
    s = re.sub(r'\s+', ' ', s)

    # Remove trailing long numeric sequences (transaction IDs, reference numbers)
    s = re.sub(r'/\d{6,}', '', s)

    # Clean UPI format: "UPI/MERCHANT/12345/ORDER678" → "UPI/MERCHANT"
    upi_match = re.match(r'UPI/([^/]+)', s, re.IGNORECASE)
    if upi_match:
        merchant = upi_match.group(1)
        # Keep just "UPI/MERCHANT" for clean display
        s = f"UPI/{merchant}"

    # Clean NEFT format: "NEFT-BANK-12345-NAME-EMI" → "NEFT-BANK EMI"
    neft_match = re.match(r'NEFT-([^-\s]+)', s, re.IGNORECASE)
    if neft_match and not upi_match:
        bank = neft_match.group(1)
        # Extract purpose keywords from the rest
        rest = s[len(f"NEFT-{bank}"):]
        # Remove numeric references from NEFT
        rest = re.sub(r'-\d{4,}', '', rest)
        s = f"NEFT-{bank}{rest}".strip()

    # Remove common noise patterns
    s = re.sub(r'#\d+', '', s)            # Remove "#12345" order IDs
    s = re.sub(r'Ref\s*No\s*:?\s*\d+', '', s, flags=re.IGNORECASE)  # Reference numbers
    s = re.sub(r'Txn\s*ID\s*:?\s*\d+', '', s, flags=re.IGNORECASE)  # Transaction IDs
    s = re.sub(r'\s+-\s+\d+$', '', s)     # Trailing " - 12345"

    return s.strip()


def scrub_pii(text: str) -> str:
    """Remove PII (Personal Identifiable Information) from text before sending to AI.
    
    Replaces: card numbers, Aadhaar, PAN, phone, email, account numbers.
    """
    if not text:
        return ""

    for pattern, replacement in PII_PATTERNS:
        text = pattern.sub(replacement, text)

    return text


def normalize_merchant_name(desc: str) -> str:
    """Extract and normalize the merchant name from a description.
    
    Used for recurring payment detection grouping.
    """
    if not desc:
        return ""

    # UPI format: "UPI/SWIGGY" → "SWIGGY"
    upi_match = re.match(r'UPI/([^/]+)', desc, re.IGNORECASE)
    if upi_match:
        return upi_match.group(1).upper().strip()

    # EMI format: "EMI-HDFC HOME LOAN" → "HDFC HOME LOAN"
    emi_match = re.match(r'EMI[_-](.+)', desc, re.IGNORECASE)
    if emi_match:
        return emi_match.group(1).upper().strip()

    # NEFT format
    neft_match = re.match(r'NEFT[_-](.+)', desc, re.IGNORECASE)
    if neft_match:
        return neft_match.group(1).upper().strip()

    # General: uppercase and strip noise
    normalized = desc.upper().strip()
    # Remove common suffix noise
    normalized = re.sub(r'\s*(CREDIT|DEBIT|PAYMENT|TRANSFER|REFUND)$', '', normalized, flags=re.IGNORECASE)

    return normalized
