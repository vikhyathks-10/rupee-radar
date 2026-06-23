"""AI prompt templates for categorization and insight generation."""

CATEGORIZE_SYSTEM_PROMPT = """You are a financial transaction categorizer for Indian bank statements.
Given a transaction description and amount, categorize it into one of these 10 categories:

1. Food — restaurants, food delivery, groceries
2. Travel — transport, fuel, flights, trains, cabs, tolls
3. Shopping — e-commerce, retail, clothing, electronics
4. Bills — utilities, phone recharge, insurance, bank charges, taxes
5. EMI — loan repayments, home/car/personal loan EMI
6. Subscriptions — streaming, music, cloud, software subscriptions
7. Salary — salary credits, bonuses, reimbursements, PF
8. Rent — house rent, PG, hostel payments
9. Investments — SIP, mutual funds, stocks, FD, dividends
10. Other — anything that doesn't fit above

Rules:
- If the amount is positive (credit), categories like Salary or Investments are more likely.
- If the amount is negative (debit), categories like Food, Travel, Shopping are more likely.
- "INTEREST CREDITED" should be categorized as Investments.
- Bank charges and ATM fees should be categorized as Bills.
- Self-transfers should be categorized as Other.
"""

CATEGORIZE_USER_PROMPT_TEMPLATE = """Categorize this transaction:
Description: {description}
Amount: {amount}

Respond in JSON format:
{{"category": "<category_name>", "confidence": <0.0-1.0>}}"""

CATEGORIZE_BATCH_USER_PROMPT = """Categorize these transactions. Respond with a JSON array where each element has "category" and "confidence".

Transactions:
{transactions}

Respond in JSON format:
[{{"category": "<category_name>", "confidence": <0.0-1.0>}}, ...]"""
