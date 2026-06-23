"""Date parsing and normalization utilities for Indian bank statement formats."""

import re
from datetime import date, datetime
from typing import Optional


# Common Indian date formats to try (ordered by likelihood)
DATE_FORMATS = [
    "%d/%m/%Y",    # 01/02/2025 (DD/MM/YYYY — Indian standard)
    "%d-%m-%Y",    # 01-02-2025
    "%Y-%m-%d",    # 2025-02-01 (ISO format)
    "%m/%d/%Y",    # 02/01/2025 (US format — fallback)
    "%d %b %Y",    # 01 Jan 2025
    "%b %d, %Y",   # Jan 01, 2025
    "%d/%m/%y",    # 01/02/25 (short year)
    "%d-%m-%y",    # 01-02-25
    "%Y%m%d",      # 20250201 (compact)
]


def parse_date(date_str: str) -> Optional[date]:
    """Parse a date string into a Python date object.
    
    Tries multiple common Indian formats. Returns None if parsing fails.
    """
    if not date_str or not date_str.strip():
        return None

    date_str = date_str.strip()

    # Strip time component if present
    date_str = re.sub(r'\s+\d{1,2}:\d{2}(:\d{2})?', '', date_str).strip()

    for fmt in DATE_FORMATS:
        try:
            parsed = datetime.strptime(date_str, fmt).date()
            # Sanity check: year should be reasonable (1900–2100)
            if 1900 <= parsed.year <= 2100:
                return parsed
        except ValueError:
            continue

    return None


def normalize_date_to_iso(d: date) -> str:
    """Convert a date to ISO 8601 string (YYYY-MM-DD)."""
    return d.strftime("%Y-%m-%d")
