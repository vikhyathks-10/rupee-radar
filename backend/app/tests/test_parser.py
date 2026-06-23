import os
import tempfile
import pytest
from app.services.parser import detect_encoding, normalize_csv_headers, parse_csv, is_transaction_row

def test_detect_encoding():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as f:
        f.write("date,description,amount\n2023-01-01,Test,100")
        name = f.name
    try:
        encoding = detect_encoding(name)
        assert encoding.lower() in ("utf-8", "ascii")
    finally:
        os.remove(name)

def test_normalize_csv_headers():
    headers = ["Txn Date", "Narration", "Withdrawal (Dr)", "Deposit (Cr)", "Chq/Ref No"]
    mapping = normalize_csv_headers(headers)
    assert mapping["Txn Date"] == "date"
    assert mapping["Narration"] == "description"
    assert mapping["Withdrawal (Dr)"] == "debit_amount"
    assert mapping["Deposit (Cr)"] == "credit_amount"

def test_is_transaction_row():
    # Valid transaction row
    assert is_transaction_row({"date": "2023-01-01", "amount": "100", "description": "UPI/Netflix"}) is True
    # Missing date
    assert is_transaction_row({"date": "", "amount": "100", "description": "UPI/Netflix"}) is False
    # Opening Balance header row
    assert is_transaction_row({"date": "2023-01-01", "amount": "100", "description": "OPENING BALANCE"}) is False

def test_parse_csv():
    csv_content = """Date,Description,Amount,Type
01/01/2026,UPI/Netflix,-199,Dr
02/01/2026,Salary,50000,Cr
"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, newline="") as f:
        f.write(csv_content)
        name = f.name
    try:
        results = parse_csv(name)
        assert len(results) == 2
        assert results[0]["description"] == "UPI/Netflix"
        assert results[0]["type"] == "Dr"
        assert results[1]["type"] == "Cr"
    finally:
        os.remove(name)
