"""Quick script to upload CSV and display all endpoint results."""

import httpx
import json

BASE = "http://localhost:8000"

# Upload
with open("../sample_statement_test.csv", "rb") as f:
    files = {"file": ("sample_statement_test.csv", f, "text/csv")}
    r = httpx.post(f"{BASE}/api/upload", files=files, timeout=120)

upload = r.json()
sid = upload["statement_id"]
print("=" * 60)
print("UPLOAD RESULT")
print("=" * 60)
print(json.dumps(upload, indent=2))
print()

# Transactions
r = httpx.get(f"{BASE}/api/transactions?statement_id={sid}&limit=50", timeout=30)
data = r.json()
print("=" * 60)
print(f"TRANSACTIONS (total={data['total']})")
print("=" * 60)
for t in data["transactions"]:
    flag = " [R]" if t["is_recurring"] else ""
    print(f"  {t['date']} | {t['description'][:35]:35} | {t['amount']:>10.2f} | {t['category']}{flag}")
print()

# Categories
r = httpx.get(f"{BASE}/api/categories?statement_id={sid}", timeout=30)
data = r.json()
if isinstance(data, dict) and "value" in data:
    cats = data["value"]
else:
    cats = data
print("=" * 60)
print("CATEGORIES (spending breakdown)")
print("=" * 60)
for c in cats:
    print(f"  {c['name']:15}: Rs.{c['total']:>10,.0f}  ({c['percentage']}%)  [{c['count']} txns]")
print()

# Recurring
r = httpx.get(f"{BASE}/api/recurring?statement_id={sid}", timeout=30)
data = r.json()
if isinstance(data, dict) and "value" in data:
    recs = data["value"]
else:
    recs = data
print("=" * 60)
print(f"RECURRING PAYMENTS ({len(recs)} detected)")
print("=" * 60)
for i in recs:
    print(f"  {i['merchant']:30}: Rs.{abs(i['amount']):>8,.0f} x{i['occurrences']} ({i['frequency']}) annual=Rs.{i['annual_cost']:>10,.0f} next={i['next_expected_date']}")
print()

# Metrics
r = httpx.get(f"{BASE}/api/metrics?statement_id={sid}", timeout=30)
m = r.json()
print("=" * 60)
print("METRICS")
print("=" * 60)
print(f"  Total Income:  Rs.{m['total_income']:>12,.2f}")
print(f"  Total Spend:   Rs.{m['total_spend']:>12,.2f}")
print(f"  Savings:       Rs.{m['savings']:>12,.2f}  ({m['savings_rate']}%)")
print()
print("  Monthly Breakdown:")
for mb in m["monthly_breakdown"]:
    print(f"    {mb['month']}: Income Rs.{mb['income']:>10,.0f}, Spend Rs.{mb['spend']:>10,.0f}")
print()

# Insights
r = httpx.get(f"{BASE}/api/insights?statement_id={sid}", timeout=30)
data = r.json()
ins = data.get("insights", data) if isinstance(data, dict) else data
print("=" * 60)
print(f"INSIGHTS ({len(ins)} generated)")
print("=" * 60)
for i in ins:
    print(f"  [{i['severity'].upper()}] {i['title']}")
    desc = i['description'].replace('\u20b9', 'Rs.').replace('₹', 'Rs.')
    print(f"    {desc[:130]}")
    if i.get("amount_referenced"):
        print(f"    Amount: Rs.{i['amount_referenced']:,.2f}")
print()

# PDF
r = httpx.get(f"{BASE}/api/report/pdf?statement_id={sid}", timeout=30)
print("=" * 60)
print("PDF REPORT")
print("=" * 60)
print(f"  Status: {r.status_code}")
print(f"  Size: {len(r.content)} bytes")
print(f"  Type: {r.headers.get('content-type')}")
print(f"  Filename: {r.headers.get('content-disposition')}")
