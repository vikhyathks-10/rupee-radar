"""Bank statement parser — extracts raw transaction rows from CSV and PDF files."""

import csv
import io
import logging
import os
import re
import chardet
import pdfplumber
from typing import Optional

logger = logging.getLogger(__name__)


def detect_encoding(file_path: str) -> str:
    """Detect the character encoding of a file."""
    with open(file_path, "rb") as f:
        raw = f.read(10000)
    result = chardet.detect(raw)
    return result.get("encoding", "utf-8") or "utf-8"


def detect_delimiter(file_path: str, encoding: str) -> str:
    """Auto-detect CSV delimiter."""
    with open(file_path, "r", encoding=encoding, errors="replace") as f:
        sample = f.read(2048)
    try:
        dialect = csv.Sniffer().sniff(sample)
        return dialect.delimiter
    except csv.Error:
        return ","


def is_transaction_row(row: dict) -> bool:
    """Check if a row looks like a real transaction (has date + amount)."""
    date_val = row.get("date", "").strip()
    amount_val = row.get("amount", "").strip()
    # A transaction row must have a non-empty date and amount
    if not date_val or not amount_val:
        return False
    # Skip common non-transaction header keywords
    desc = row.get("description", "").upper()
    skip_keywords = ["BALANCE", "OPENING", "CLOSING", "B/F", "BROUGHT FORWARD", "CARRY FORWARD"]
    for kw in skip_keywords:
        if kw in desc:
            return False
    return True


def normalize_csv_headers(headers: list[str]) -> dict:
    """Map CSV headers to standard field names by detecting data patterns.
    
    Returns a mapping: {original_header: standard_name}
    Standard names: date, description, amount, type (debit/credit indicator)
    """
    mapping = {}
    for h in headers:
        h_lower = h.lower().strip()
        if any(kw in h_lower for kw in ["date", "txn date", "transaction date", "trans date", "value date", "posting date"]):
            mapping[h] = "date"
        elif any(kw in h_lower for kw in ["desc", "description", "narration", "particulars", "remarks", "details", "transaction"]):
            mapping[h] = "description"
        elif any(kw in h_lower for kw in ["amount", "withdrawal", "deposit", "credit", "debit", "dr", "cr", "balance"]):
            # Handle separate credit/debit columns
            if "credit" in h_lower or "cr" in h_lower or "deposit" in h_lower:
                mapping[h] = "credit_amount"
            elif "debit" in h_lower or "dr" in h_lower or "withdrawal" in h_lower:
                mapping[h] = "debit_amount"
            else:
                mapping[h] = "amount"
        elif any(kw in h_lower for kw in ["type", "dr/cr", "debit/credit", "txn type"]):
            mapping[h] = "type"

    return mapping


def parse_csv(file_path: str) -> list[dict]:
    """Parse a CSV bank statement into raw transaction row dicts.
    
    Each dict contains: date, description, amount, type (Cr/Dr indicator).
    """
    encoding = detect_encoding(file_path)
    delimiter = detect_delimiter(file_path, encoding)

    transactions = []
    with open(file_path, "r", encoding=encoding, errors="replace") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        if not reader.fieldnames:
            return []

        header_map = normalize_csv_headers(reader.fieldnames)

        for row in reader:
            mapped = {}
            for orig, standard in header_map.items():
                val = row.get(orig, "").strip()
                if standard == "credit_amount":
                    mapped["credit_amount"] = val
                elif standard == "debit_amount":
                    mapped["debit_amount"] = val
                else:
                    mapped[standard] = val

            # Handle separate credit/debit columns → unified amount + type
            if "credit_amount" in mapped and "debit_amount" in mapped:
                cr = mapped.get("credit_amount", "")
                dr = mapped.get("debit_amount", "")
                if cr and cr not in ("0", "0.00", "-", "", "N/A"):
                    mapped["amount"] = cr
                    mapped["type"] = "Cr"
                elif dr and dr not in ("0", "0.00", "-", "", "N/A"):
                    mapped["amount"] = dr
                    mapped["type"] = "Dr"
                else:
                    continue  # Both empty — skip
                del mapped["credit_amount"]
                del mapped["debit_amount"]

            # Fill missing fields with defaults
            mapped.setdefault("date", "")
            mapped.setdefault("description", "")
            mapped.setdefault("amount", "")
            mapped.setdefault("type", "")

            if is_transaction_row(mapped):
                transactions.append(mapped)

    return transactions


def parse_pdf(file_path: str) -> list[dict]:
    """Parse a PDF bank statement into raw transaction row dicts.
    
    Uses pdfplumber to extract table data. Falls back gracefully if extraction fails.
    """
    transactions = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if not table:
                    continue

                # First row might be header
                headers = None
                for i, row in enumerate(table):
                    if i == 0:
                        # Try to use as headers
                        clean_headers = [str(c).strip() if c else f"col_{j}" for j, c in enumerate(row)]
                        header_map = normalize_csv_headers(clean_headers)
                        if header_map:
                            headers = clean_headers
                            continue
                        else:
                            # No recognizable headers — treat as data row with positional columns
                            headers = [f"col_{j}" for j in range(len(row))]

                    # Process data rows
                    row_dict = {}
                    for j, cell in enumerate(row):
                        header = headers[j] if j < len(headers) else f"col_{j}"
                        row_dict[header] = str(cell).strip() if cell else ""

                    if headers and header_map:
                        mapped = {}
                        for orig, standard in header_map.items():
                            mapped[standard] = row_dict.get(orig, "")
                        mapped.setdefault("date", "")
                        mapped.setdefault("description", "")
                        mapped.setdefault("amount", "")
                        mapped.setdefault("type", "")
                    else:
                        # Fallback: positional mapping (date=0, desc=1, amount=2, type=3)
                        vals = [str(c).strip() if c else "" for c in row]
                        mapped = {
                            "date": vals[0] if len(vals) > 0 else "",
                            "description": vals[1] if len(vals) > 1 else "",
                            "amount": vals[2] if len(vals) > 2 else "",
                            "type": vals[3] if len(vals) > 3 else "",
                        }

                    if is_transaction_row(mapped):
                        transactions.append(mapped)

    except Exception as e:
        # If PDF parsing fails, raise so the pipeline can report the error
        logger.error(f"PDF parsing failed for {file_path}: {e}")
        raise ValueError(f"Could not parse PDF file: {e}")

    return transactions


def parse_statement(file_path: str) -> list[dict]:
    """Parse a bank statement file (CSV or PDF) into raw transaction dicts.
    
    Returns list of dicts with keys: date, description, amount, type.
    Raises ValueError if the file is corrupted or unreadable.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".csv":
        result = parse_csv(file_path)
        if not result:
            raise ValueError("No valid transactions found in CSV file. The file may be empty, have unrecognized headers, or contain only non-transaction rows.")
        return result
    elif ext == ".pdf":
        return parse_pdf(file_path)  # parse_pdf raises ValueError on failure
    else:
        raise ValueError(f"Unsupported file extension '{ext}'. Only CSV and PDF files are accepted.")
