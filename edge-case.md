# RupeeRadar — Edge Cases & Corner Cases

This document catalogs every known edge case and corner case for the RupeeRadar project, organized by pipeline stage and system layer. Each case includes: the scenario, expected behavior, handling strategy, and which service/file should implement it.

---

## 1. File Upload & Parsing Edge Cases

### 1.1 File Format Edge Cases

| # | Scenario | Expected Behavior | Handling | Service/File |
|---|----------|-------------------|----------|--------------|
| 1.1.1 | User uploads an Excel file (.xlsx) | Reject with 400 error listing supported formats (CSV, PDF) | Validate extension before parsing | `upload.py`, `parser.py` |
| 1.1.2 | User uploads a text file (.txt) masquerading as CSV | Attempt CSV parse; if it fails, reject with 422 | Detect malformed CSV during parsing | `parser.py` |
| 1.1.3 | User uploads an image file (.jpg/.png) | Reject immediately with 400 | Extension whitelist check | `upload.py` |
| 1.1.4 | User uploads a very large file (>50MB) | Reject with 413 Payload Too Large | Set max upload size in FastAPI config | `upload.py`, `main.py` |
| 1.1.5 | User uploads an empty file (0 bytes) | Reject with 400 "Empty file" | Check file size after saving | `upload.py` |
| 1.1.6 | User uploads a password-protected PDF | Reject with 422 "Encrypted PDF not supported" | pdfplumber will throw; catch and return error | `parser.py` |
| 1.1.7 | User uploads a scanned PDF (no extractable text) | Reject with 422 "No text content found in PDF" | Check if extracted rows = 0 after pdfplumber | `parser.py` |
| 1.1.8 | File has no extension in filename | Attempt to detect format by content (peek first bytes); if uncertain, reject with 400 | Content sniffing: check for PDF magic bytes `%PDF-` or CSV comma patterns | `parser.py` |
| 1.1.9 | Filename contains special characters or Unicode | Save with sanitized filename; process normally | Strip/sanitize filename before saving to disk | `upload.py` |
| 1.1.10 | Filename is extremely long (>255 chars) | Truncate filename; process normally | Truncate to 255 chars with preserved extension | `upload.py` |

### 1.2 CSV-Specific Edge Cases

| # | Scenario | Expected Behavior | Handling | Service/File |
|---|----------|-------------------|----------|--------------|
| 1.2.1 | CSV has inconsistent delimiters (mix of commas and tabs) | Attempt to auto-detect delimiter; fall back to comma default | Use csv.Sniffer or pandas delimiter detection | `parser.py` |
| 1.2.2 | CSV has no header row | Attempt headerless parse with positional columns; if column count matches expected, proceed | Support configurable "has_header" flag | `parser.py` |
| 1.2.3 | CSV header row is in a non-standard language (Hindi, regional) | Look for known column patterns (date-like, amount-like, text-like) regardless of header names | Column detection by data pattern, not header text | `parser.py` |
| 1.2.4 | CSV has extra metadata rows at the top (bank name, account summary) | Skip non-transaction rows until first recognizable transaction row | Detect transaction row pattern (has date + amount) | `parser.py` |
| 1.2.5 | CSV has footer rows (summary totals, closing balance) | Skip rows after last recognizable transaction row | Stop parsing when rows no longer match transaction pattern | `parser.py` |
| 1.2.6 | CSV uses different date formats in different rows | Normalize each date individually; log format variations | `date_utils.py` tries multiple formats per row | `date_utils.py`, `parser.py` |
| 1.2.7 | CSV has quoted fields with commas inside | Parse correctly using proper CSV quoting rules | Python csv module handles this by default | `parser.py` |
| 1.2.8 | CSV has different encodings (UTF-8, UTF-16, ANSI) | Auto-detect encoding; re-decode if needed | Use chardet or try UTF-8 → Latin-1 fallback | `parser.py` |
| 1.2.9 | CSV has Windows line endings (\r\n) mixed with Unix (\n) | Parse correctly regardless | Python csv module handles mixed line endings | `parser.py` |
| 1.2.10 | CSV columns are in unexpected order | Map columns by detected type, not by position | Pattern-based column detection | `parser.py` |

### 1.3 PDF-Specific Edge Cases

| # | Scenario | Expected Behavior | Handling | Service/File |
|---|----------|-------------------|----------|--------------|
| 1.3.1 | PDF has multi-page statement with page headers/footers on each page | Extract all pages; skip repeated header/footer text | pdfplumber page-by-page extraction; filter header rows | `parser.py` |
| 1.3.2 | PDF table has merged cells or spanning rows | Best-effort extraction; flag uncertain rows | pdfplumber handles basic merged cells; log warnings | `parser.py` |
| 1.3.3 | PDF has two tables side-by-side on one page | Extract the correct table (the transaction table); ignore side content | Target specific table by position or content pattern | `parser.py` |
| 1.3.4 | PDF uses a non-standard font that maps numbers incorrectly | Amounts may be garbled; flag statement as potentially corrupted | Validate extracted amounts are numeric; reject if >50% fail | `parser.py` |
| 1.3.5 | PDF has watermark text overlapping transaction rows | Best-effort extraction; noisy descriptions cleaned later | Clean step will strip known watermark patterns | `parser.py`, `cleaner.py` |

---

## 2. Transaction Cleaning Edge Cases

### 2.1 Date Parsing Edge Cases

| # | Scenario | Expected Behavior | Handling | Service/File |
|---|----------|-------------------|----------|--------------|
| 2.1.1 | Date is "01/02/2025" — ambiguous (Jan 2 or Feb 1?) | Default to DD/MM/YYYY (Indian convention); configurable | Try DD/MM/YYYY first; if fails, try MM/DD/YYYY | `date_utils.py` |
| 2.1.2 | Date uses Indian format: "15-01-2025" (DD-MM-YYYY) | Parse correctly to 2025-01-15 | Support hyphen-separated DD-MM-YYYY | `date_utils.py` |
| 2.1.3 | Date has no year: "15/01" or "Jan 15" | Infer year from statement upload date or surrounding transactions | Use upload year; validate consistency with neighboring rows | `date_utils.py` |
| 2.1.4 | Date uses text month: "January 15, 2025" or "15 Jan 2025" | Parse correctly | Support multiple text month formats | `date_utils.py` |
| 2.1.5 | Date field is empty or null | Skip row with warning log | Flag row as invalid; continue processing | `cleaner.py` |
| 2.1.6 | Date is clearly invalid: "99/99/9999" or "00/00/0000" | Skip row with warning log | Date validation: reject impossible dates | `date_utils.py`, `cleaner.py` |
| 2.1.7 | Date is in future (beyond upload date) | Flag as suspicious; still parse but log warning | Allow future dates up to +30 days (pending transactions) | `date_utils.py` |
| 2.1.8 | Multiple date formats used within same statement | Parse each individually; normalize all to ISO 8601 | Per-row format detection with caching | `date_utils.py` |
| 2.1.9 | Date has time component: "2025-01-15 14:30:00" | Strip time; keep only date portion | Split on space; take first part | `date_utils.py` |
| 2.1.10 | Transaction dated on bank holiday or weekend | Process normally — no special handling needed | No action; holidays don't affect categorization | — |

### 2.2 Amount Parsing Edge Cases

| # | Scenario | Expected Behavior | Handling | Service/File |
|---|----------|-------------------|----------|--------------|
| 2.2.1 | Amount uses Indian comma format: "1,23,456.00" (lakhs/crores) | Parse correctly to 123456.00 | Remove commas respecting Indian grouping pattern | `currency_utils.py` |
| 2.2.2 | Amount has currency symbol: "₹1,234" or "Rs. 1,234" or "INR 1234" | Strip symbol; parse numeric portion | Regex to strip ₹/Rs./INR prefixes | `currency_utils.py` |
| 2.2.3 | Amount is negative with parentheses: "(1,234)" — accounting notation | Convert to -1234.00 | Detect parenthesized amounts → negate | `currency_utils.py` |
| 2.2.4 | Amount has trailing "Cr" or "Dr" indicator: "1234 Cr" | Convert Cr → positive, Dr → negative | Detect Cr/Dr suffix; assign sign | `currency_utils.py` |
| 2.2.5 | Separate credit and debit columns instead of signed amounts | Parse both columns; merge into single signed amount field | If two amount columns: credit as positive, debit as negative | `parser.py`, `currency_utils.py` |
| 2.2.6 | Amount is zero: "0.00" | Keep as valid transaction (could be a balance check or free trial) | Allow zero amounts; they contribute nothing to metrics | `cleaner.py` |
| 2.2.7 | Amount field is empty or null | Skip row with warning log | Flag as invalid row | `cleaner.py` |
| 2.2.8 | Amount is non-numeric: "N/A" or "—" | Skip row with warning log | Numeric validation | `currency_utils.py`, `cleaner.py` |
| 2.2.9 | Amount has extra whitespace or embedded spaces: "1 234.00" | Remove spaces; parse correctly | Strip all whitespace from amount string | `currency_utils.py` |
| 2.2.10 | Very large amount: >10,00,00,000 (₹10 crore) | Process normally but flag for review in insights | Log warning; still process | `cleaner.py`, `insight_generator.py` |
| 2.2.11 | Amount appears to be in wrong scale (e.g., 0.45 instead of 450) | Flag as suspicious but process as-is; don't auto-correct | No auto-scaling — too risky; user should verify | `cleaner.py` |

### 2.3 Description Cleaning Edge Cases

| # | Scenario | Expected Behavior | Handling | Service/File |
|---|----------|-------------------|----------|--------------|
| 2.3.1 | Description is entirely numeric: "1234567890" (just a ref number) | Categorize as "Other"; attempt AI classification | AI receives numeric-only; likely returns "Other" | `categorizer.py` |
| 2.3.2 | Description is very long (>200 chars) | Truncate for display; keep full for AI categorization | Store original; use truncated for display | `cleaner.py` |
| 2.3.3 | Description contains only bank codes: "NEFT/RTGS/IMPS" with no merchant name | Best-effort categorization; likely "Other" or "Bills" | AI handles this case | `categorizer.py` |
| 2.3.4 | Description has mixed languages (English + Hindi transliteration) | Clean and process; AI handles multilingual input | Keep original; AI understands transliteration | `cleaner.py`, `categorizer.py` |
| 2.3.5 | Description contains emoji or special Unicode characters | Strip emojis; keep relevant text | Regex filter for non-text Unicode | `text_utils.py` |
| 2.3.6 | Description is "BALANCE B/F" or "OPENING BALANCE" | Skip non-transaction rows | Filter known non-transaction keywords | `cleaner.py` |
| 2.3.7 | Description is "INTEREST CREDITED" or "ATM CHARGE REVERSAL" | Categorize as "Investments" or "Other" respectively | Rule-based mapping for bank-generated entries | `categorizer.py`, `category_keywords.json` |
| 2.3.8 | Description has UPI format: "UPI/PAYTM/123456/John/Ref123" | Extract merchant ("PAYTM"), clean rest → "Paytm Payment" | UPI description parser: split on "/" and extract merchant | `text_utils.py`, `cleaner.py` |
| 2.3.9 | Description has NEFT format: "NEFT-HDFC-12345-RAHUL-EMI" | Extract key info → "HDFC EMI Payment" | NEFT description parser: extract bank + purpose | `text_utils.py`, `cleaner.py` |
| 2.3.10 | Description is entirely empty or whitespace | Skip row with warning | Flag as invalid | `cleaner.py` |

### 2.4 Deduplication Edge Cases

| # | Scenario | Expected Behavior | Handling | Service/File |
|---|----------|-------------------|----------|--------------|
| 2.4.1 | Two transactions with same date, amount, description | Treat as duplicate; keep one | Exact match dedup on (date, amount, description) | `cleaner.py` |
| 2.4.2 | Same transaction appears in both credit and debit columns | If amounts are same positive and negative, it's a reversal; keep only the net effect | Detect reversal pairs; remove the debit, keep credit (or vice versa depending on intent) | `cleaner.py` |
| 2.4.3 | Two similar but not identical descriptions: "SWIGGY ORDER 123" vs "SWIGGY ORDER 456" | Treat as separate transactions (different orders) | Do not deduplicate on partial description match | `cleaner.py` |
| 2.4.4 | Transaction reversed on same day (purchase + refund) | Keep both; metrics will net them out | Don't deduplicate; both are real events | `cleaner.py` |
| 2.4.5 | Same EMI payment appears twice in same month (duplicate bank entry) | Deduplicate if date + amount + description match exactly | Exact dedup handles this | `cleaner.py` |

---

## 3. Categorization Edge Cases

### 3.1 Rule-Based Categorization Edge Cases

| # | Scenario | Expected Behavior | Handling | Service/File |
|---|----------|-------------------|----------|--------------|
| 3.1.1 | Description matches multiple keyword rules (e.g., "AMAZON PRIME" → Shopping vs Subscriptions) | Use most specific match; "PRIME" → Subscriptions wins over "AMAZON" → Shopping | Priority-ordered keyword matching; longer/specific matches first | `categorizer.py`, `category_keywords.json` |
| 3.1.2 | Description contains keyword but in wrong context (e.g., "AMAZON REFUND") | Detect "REFUND" override; keep original category but mark as credit reversal | Refund keyword overrides: if "REFUND"/"REVERSAL" found, keep category but note reversal | `categorizer.py` |
| 3.1.3 | New merchant not in keyword dictionary | Fall through to AI categorization | Uncategorized items queued for AI | `categorizer.py` |
| 3.1.4 | Description has merchant name but also PII (e.g., "UPI/NETFLIX/9876543210/Arun Kumar") | Strip PII before matching; match on "NETFLIX" | PII scrubbed before keyword lookup | `text_utils.py`, `categorizer.py` |
| 3.1.5 | Description uses abbreviations: "AMZN" instead of "AMAZON" | Add abbreviation aliases to keyword dictionary | Include common abbreviations in `category_keywords.json` | `category_keywords.json` |
| 3.1.6 | Category keyword conflict: "GROCERY" could be Food or Shopping | Map to "Food" as more specific category; add sub-priority | Disambiguation priority list in keywords config | `category_keywords.json` |
| 3.1.7 | Description is a bank fee: "ATM DECLINE CHARGE" or "MIN BALANCE PENALTY" | Categorize as "Bills" (or specific "Bank Charges" sub-category mapped to Bills) | Add bank charge keywords → Bills | `category_keywords.json` |
| 3.1.8 | Transaction is a self-transfer between own accounts | Categorize as "Other" with sub-label "Self Transfer"; exclude from income/spend metrics | Detect self-transfer patterns (same person name in description) | `categorizer.py`, `metrics_calculator.py` |

### 3.2 AI Categorization Edge Cases

| # | Scenario | Expected Behavior | Handling | Service/File |
|---|----------|-------------------|----------|--------------|
| 3.2.1 | OpenAI API returns a category not in the defined 10 categories | Map to closest valid category; if impossible, use "Other" | Validate AI response against allowed categories; remap or default to Other | `categorize_chain.py` |
| 3.2.2 | OpenAI API returns null/empty response for a transaction | Assign "Other"; log the failure | Default to Other on empty response | `categorize_chain.py` |
| 3.2.3 | OpenAI API returns low confidence (<0.5) for a transaction | Assign category but flag for user review; still include in metrics | Store confidence; mark low-confidence items | `categorize_chain.py` |
| 3.2.4 | OpenAI API is completely unavailable (network failure) | Fall back to rule-only categorization; all unmatched get "Other" | Graceful degradation; log error; continue pipeline | `categorizer.py`, `openai_client.py` |
| 3.2.5 | OpenAI API is rate-limited (429 error) | Retry with exponential backoff (3 attempts); then fall back to "Other" for remaining | Retry logic: 1s → 2s → 4s delays; then give up | `openai_client.py` |
| 3.2.6 | Batch of 20 uncategorized transactions sent to AI — one response is malformed | Parse valid responses; skip malformed ones (assign "Other") | Per-item validation in batch response parsing | `categorize_chain.py` |
| 3.2.7 | AI categorization takes >30 seconds total | Show processing progress; complete pipeline even if slow | Async processing; progress updates via status field | `processing_pipeline.py` |
| 3.2.8 | Same description sent to AI twice (different amounts) | Cache hit by normalized description; reuse category from first call | Cache keyed on normalized description (amount-independent) | `categorizer.py` |
| 3.2.9 | AI returns "Salary" for a transaction that looks like freelance income | Accept AI classification; "Salary" covers all regular income | No special handling; Salary = regular income in this context | `categorize_chain.py` |
| 3.2.10 | AI returns "EMI" for what is actually a loan disbursement (credit) | Validate: EMI should typically be debit; if credit → remap to "Other" or "Investments" | Cross-validate: category + amount sign consistency check | `categorizer.py` |

---

## 4. Recurring Detection Edge Cases

| # | Scenario | Expected Behavior | Handling | Service/File |
|---|----------|-------------------|----------|--------------|
| 4.1 | Only 1 occurrence of a known recurring merchant (e.g., first Netflix payment) | Flag as "potential recurring" (not confirmed); don't include in annual cost projection | Single occurrence → "potential" status; need ≥2 for "confirmed" | `recurring_detector.py` |
| 4.2 | Recurring payment amount changed (Netflix ₹499 → ₹649 after price hike) | Still detect as recurring; note amount change; use latest amount for projection | Allow ±10% tolerance; if beyond, update amount and flag change | `recurring_detector.py` |
| 4.3 | Recurring payment skipped a month (user paused subscription) | Don't break detection if gap is 2x the normal interval (one skip allowed) | Allow one missed interval before breaking recurring status | `recurring_detector.py` |
| 4.4 | Two different recurring payments from same merchant (e.g., 2 SIPs from same fund house) | Distinguish by amount; treat as separate recurring items | Group by (merchant + amount) instead of merchant alone | `recurring_detector.py` |
| 4.5 | Annual payment (insurance premium) — only appears once in 3-month statement | Flag as "potential recurring" with frequency "annual"; cannot confirm with 1 occurrence | Note as likely annual; low confidence | `recurring_detector.py` |
| 4.6 | Recurring payment date shifted by a few days each month (e.g., 1st → 3rd → 5th) | Still detect as recurring (±5 day tolerance per architecture) | Interval consistency with tolerance handles this | `recurring_detector.py` |
| 4.7 | One-time purchase at a merchant that also has recurring (e.g., Amazon Prime subscription + one-time Amazon order) | Separate recurring and one-time by amount consistency | Amazon ₹499 monthly = recurring; Amazon ₹2,345 one-time = not recurring | `recurring_detector.py` |
| 4.8 | Salary deposit appears on different dates (e.g., last working day varies) | Detect as recurring with date tolerance; frequency = monthly | ±5 day tolerance for salary dates | `recurring_detector.py` |
| 4.9 | Rent paid via different methods each month (UPI, cheque, bank transfer) — descriptions differ | Group by amount consistency + keyword "rent" instead of merchant name alone | Keyword-based grouping supplement for known recurring types | `recurring_detector.py`, `recurring_rules.py` |
| 4.10 | Statement covers only 1 month — insufficient data for recurring detection | Detect known recurring merchants by name; mark others as "potential" | Limited data mode: rely more on merchant name matching | `recurring_detector.py` |
| 4.11 | EMIs that decrease over time (reducing balance EMI) | Detect as recurring despite amount variation; flag as "variable amount EMI" | Allow wider amount tolerance for EMI-flagged items; track trend | `recurring_detector.py` |

---

## 5. Metrics Calculation Edge Cases

| # | Scenario | Expected Behavior | Handling | Service/File |
|---|----------|-------------------|----------|--------------|
| 5.1 | Total spend exceeds total income (negative savings) | Show savings as negative; savings rate as negative percentage; generate "critical" insight | Allow negative values; no special clamping | `metrics_calculator.py` |
| 5.2 | Zero income transactions in statement (only debit transactions) | Total income = 0; savings rate undefined (0/0); show as "N/A" or "—" | Handle division by zero: savings_rate = None when income = 0 | `metrics_calculator.py` |
| 5.3 | Zero spend transactions (only credit/salary entries) | Total spend = 0; savings = total income; savings rate = 100% | Valid scenario; process normally | `metrics_calculator.py` |
| 5.4 | All transactions categorized as "Other" | Top categories list shows only "Other"; still compute metrics | Valid; insights will flag poor categorization | `metrics_calculator.py` |
| 5.5 | Single transaction in entire statement | Process normally; metrics reflect one transaction | No minimum transaction count required | `metrics_calculator.py` |
| 5.6 | Self-transfers between own accounts inflate income/spend totals | Exclude self-transfers from income/spend calculations | Filter out "Self Transfer" category before computing | `metrics_calculator.py` |
| 5.7 | Statement spans multiple years | Group monthly breakdown by year-month; handle year boundaries correctly | "2024-12" and "2025-01" are separate months | `metrics_calculator.py` |
| 5.8 | Very large number of categories (>10 due to sub-categories leaking in) | Force top 10 categories; merge rare ones into "Other" if below threshold | Cap category display; sub-threshold → Other | `metrics_calculator.py` |
| 5.9 | Category percentages don't sum to 100% due to rounding | Show actual percentages; add note "percentages may not sum to 100% due to rounding" | Don't force rounding adjustment; let actual values show | `metrics_calculator.py` |
| 5.10 | Biggest transaction is actually income (large salary deposit) | Show biggest debit transaction separately from biggest credit; clarify "biggest spend" vs "biggest income" | Separate "biggest spend" and "biggest income" lists | `metrics_calculator.py` |
| 5.11 | Opening/closing balance rows present in data | Skip balance rows; they are not transactions | Filter known balance keywords | `cleaner.py`, `metrics_calculator.py` |

---

## 6. Insight Generation Edge Cases

| # | Scenario | Expected Behavior | Handling | Service/File |
|---|----------|-------------------|----------|--------------|
| 6.1 | OpenAI returns insights referencing amounts not in the actual data | Discard such insights; regenerate or replace with data-accurate ones | Validate insight amounts against actual metrics before accepting | `insight_generator.py` |
| 6.2 | OpenAI returns fewer than 3 insights | Retry with modified prompt; if still <3, supplement with template-based insights | Minimum 3 insights: AI + fallback templates | `insight_generator.py` |
| 6.3 | OpenAI returns more than 5 insights | Keep top 5 by severity priority (critical > warning > info) | Truncate to 5 | `insight_generator.py` |
| 6.4 | OpenAI returns generic advice ("save more money") without specific data references | Discard; regenerate with stricter prompt emphasizing data-grounded insights | Prompt refinement: "never give generic advice" | `prompts.py`, `insight_generator.py` |
| 6.5 | All spending is in one category (100% Food) | Generate insight about concentration risk; suggest diversification awareness | Single-category dominance is a valid insight trigger | `insight_generator.py` |
| 6.6 | Statement has very few transactions (<5) | Generate limited insights acknowledging small dataset; flag low confidence | Insight: "Limited data — upload more statements for better analysis" | `insight_generator.py` |
| 6.7 | Savings rate is extremely high (>80%) | Generate positive insight; also note possibility of under-reporting spend | Both "great savings" and "verify all spend is captured" | `insight_generator.py` |
| 6.8 | Savings rate is extremely negative (>-50%) | Generate critical insight about debt/spending crisis | Critical severity insight | `insight_generator.py` |
| 6.9 | OpenAI insight response is malformed JSON | Parse what's possible; fill remaining with template-based fallbacks | Graceful JSON parsing with fallback | `insight_chain.py` |
| 6.10 | OpenAI assigns unexpected severity (e.g., "critical" for a minor category) | Revalidate severity against thresholds: >50% income = critical, >30% = warning, rest = info | Severity re-calibration based on percentage thresholds | `insight_generator.py` |

---

## 7. API & Frontend Edge Cases

### 7.1 API Edge Cases

| # | Scenario | Expected Behavior | Handling | Service/File |
|---|----------|-------------------|----------|--------------|
| 7.1.1 | GET request without statement_id parameter | Return 400 "statement_id required" | Validate required query params | `transactions.py`, `metrics.py`, etc. |
| 7.1.2 | GET request with non-existent statement_id (UUID) | Return 404 "Statement not found" | DB lookup; return 404 if missing | All GET endpoints |
| 7.1.3 | GET request with statement_id of a statement still in "processing" status | Return 202 with partial data or "still processing" message | Check status; return 202 if not completed | All GET endpoints |
| 7.1.4 | GET request with statement_id of a "failed" statement | Return 422 with error details from processing_error field | Check status; return error info | All GET endpoints |
| 7.1.5 | Pagination: page parameter exceeds total pages | Return empty list with total count | Return `{ transactions: [], total: N }` | `transactions.py` |
| 7.1.6 | Category filter with invalid category name | Return 400 "Invalid category" with list of valid categories | Validate against 10 defined categories | `transactions.py` |
| 7.1.7 | Concurrent upload of same file by two requests | Process both independently; create two statement records | No conflict; each upload creates unique statement | `upload.py` |
| 7.1.8 | CORS request from non-frontend origin | Allow only frontend origin (localhost:5173) in development | FastAPI CORS middleware with whitelist | `main.py` |
| 7.1.9 | Request timeout during long AI processing | Return processing status; frontend polls until complete | Async processing; no request timeout on pipeline | `upload.py`, `processing_pipeline.py` |

### 7.2 Frontend Edge Cases

| # | Scenario | Expected Behavior | Handling | Service/File |
|---|----------|-------------------|----------|--------------|
| 7.2.1 | User navigates to /dashboard without uploading first | Show empty state: "Upload a statement to see your dashboard" | Check statement_id in store; show empty state if null | `DashboardPage.tsx` |
| 7.2.2 | User refreshes the page after upload | Statement data lost (Zustand is in-memory) — show empty state prompt | Zustand persists nothing; user re-uploads | `transactionStore.ts` |
| 7.2.3 | Upload fails (network error / 500) | Show error banner with retry option | Error state in useUpload hook; retry button | `useUpload.ts`, `FileUpload.tsx` |
| 7.2.4 | Backend is down when frontend loads | Show "Service unavailable" message on upload page | Health check on mount; display connection error | `client.ts`, `UploadPage.tsx` |
| 7.2.5 | Very slow processing (>60 seconds) | Show detailed progress steps; don't leave user wondering | Step-by-step progress bar with stage names | `FileUpload.tsx` |
| 7.2.6 | Pie chart has 10+ categories — labels overlap | Limit pie chart to top 5-7 categories; merge rest into "Other" | Top N display with "Other" bucket | `CategoryPieChart.tsx` |
| 7.2.7 | Bar chart has only 1 month of data | Show single bar; still render chart | Handle single data point gracefully | `MonthlyBarChart.tsx` |
| 7.2.8 | User uploads a second statement while viewing first | Replace data; show new statement results | Replace statement_id in store; refetch all data | `transactionStore.ts` |
| 7.2.9 | PDF download fails (browser blocks download) | Show error message with alternative: "Right-click → Save link" | Catch download error; show fallback instructions | `ReportDownload.tsx` |
| 7.2.10 | Currency formatting for amounts >1 crore | Display as "₹1.23 Cr" instead of long number | Abbreviated formatting for large amounts | `formatCurrency.ts` |

---

## 8. Database & Storage Edge Cases

| # | Scenario | Expected Behavior | Handling | Service/File |
|---|----------|-------------------|----------|--------------|
| 8.1 | SQLite database file gets corrupted | Return error on startup; suggest deleting .db to reset | Detect corruption; provide reset instructions in error message | `database.py` |
| 8.2 | SQLite database file is locked by another process | Wait with retry; if persistent, return error | SQLite busy timeout: 5 seconds | `database.py` |
| 8.3 | Upload directory doesn't exist | Create it on startup | os.makedirs on app init | `config.py`, `main.py` |
| 8.4 | Disk space full during file upload | Return 500 "Storage error"; don't proceed with processing | Catch OSError on file write | `upload.py` |
| 8.5 | Very large statement produces >10,000 transaction rows | Paginated storage and retrieval; process in chunks | Pagination in API; batch DB inserts | `transactions.py`, `processing_pipeline.py` |
| 8.6 | Concurrent DB writes from two processing pipelines | SQLite handles via WAL mode; serialized writes | Enable WAL journal mode for better concurrency | `database.py` |
| 8.7 | Statement processing fails mid-pipeline (e.g., AI fails after categorization) | Partial results saved; statement marked "failed" with error detail | Transaction rollback for failed stage; keep successful stages | `processing_pipeline.py` |

---

## 9. Security & Privacy Edge Cases

| # | Scenario | Expected Behavior | Handling | Service/File |
|---|----------|-------------------|----------|--------------|
| 9.1 | Transaction description contains Aadhaar number (12 digits) | Strip Aadhaar before AI call; replace with "AADHAAR_REF" | Regex: `\b\d{4}\s?\d{4}\s?\d{4}\b` → "AADHAAR_REF" | `text_utils.py` |
| 9.2 | Description contains PAN number (e.g., "ABCDE1234F") | Strip PAN before AI call; replace with "PAN_REF" | Regex: `\b[A-Z]{5}\d{4}[A-Z]\b` → "PAN_REF" | `text_utils.py` |
| 9.3 | Description contains phone number (10 digits) | Strip phone number; replace with "PHONE_REF" | Regex: `\b\d{10}\b` → "PHONE_REF" | `text_utils.py` |
| 9.4 | Description contains email address | Strip email; replace with "EMAIL_REF" | Regex: `\b[\w.]+@[\w.]+\.\w+\b` → "EMAIL_REF" | `text_utils.py` |
| 9.5 | Description contains credit/debit card number | Strip card number; replace with "CARD_REF" | Regex: `\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b` (but not Aadhaar) → "CARD_REF" | `text_utils.py` |
| 9.6 | Description contains a person's full name | Replace with "USER" | Known name patterns from bank format specs | `text_utils.py` |
| 9.7 | User uploads statement belonging to someone else | No auth in prototype — process anyway; note in security docs that auth is needed for production | Accept all uploads in prototype; flag in documentation | Architecture note |
| 9.8 | Uploaded file contains malware (e.g., macro-enabled PDF) | Don't execute any embedded code; pdfplumber reads safely | pdfplumber extracts text only; no code execution risk | `parser.py` |
| 9.9 | Original file not deleted after parsing (architecture says delete) | Ensure deletion happens in pipeline; if deletion fails, log warning | `os.remove` after successful parse; catch and log OSError | `processing_pipeline.py` |
| 9.10 | AI API logs contain PII that was missed by scrubber | Scrubbing is done client-side before API call; residual PII is minimal risk | Continuous improvement of scrubbing rules; audit AI request logs | `text_utils.py`, `openai_client.py` |

---

## 10. Deployment & Environment Edge Cases

| # | Scenario | Expected Behavior | Handling | Service/File |
|---|----------|-------------------|----------|--------------|
| 10.1 | OPENAI_API_KEY not set in .env | Rule-only categorization; all AI calls skipped; insights generated from templates | Detect missing key on startup; log warning; run in degraded mode | `config.py`, `openai_client.py` |
| 10.2 | OPENAI_API_KEY is invalid/expired | AI calls fail with 401; fall back to rule-only; log error | Catch 401; fall back gracefully | `openai_client.py` |
| 10.3 | Port 8000 or 5173 already in use | Docker will fail to start; show clear error | Check port availability; suggest alternate ports | `docker-compose.yml`, user instructions |
| 10.4 | Docker not installed on user's machine | Provide manual start instructions (uvicorn + npm run dev) | Dual run mode: Docker or manual | README |
| 10.5 | Python 3.11 not available (user has 3.9 or 3.12) | FastAPI works on 3.9+; adjust requirements | Pin minimum Python to 3.9 in pyproject.toml | `pyproject.toml` |
| 10.6 | Node.js version incompatible with Vite | Vite requires Node 18+; show version error | Check node version in package.json engines field | `package.json` |
| 10.7 | Windows path issues in Docker (backslash vs forward slash) | Use forward paths in all config; Docker handles Windows paths via volume mounts | All paths use forward slashes; Docker Desktop for Windows handles mounts | `docker-compose.yml`, `config.py` |
| 10.8 | OneDrive-synced folder causes file locking issues | Exclude data/ and uploads/ from OneDrive sync; or run outside OneDrive path | Recommend moving project outside OneDrive; or exclude dirs | User instructions |
| 10.9 | Large PDF upload causes Docker container OOM | Set memory limit in Docker; stream-parse instead of loading entire PDF | Docker memory limit; pdfplumber page-by-page extraction | `docker-compose.yml`, `parser.py` |

---

## 11. Cross-Cutting Edge Cases

| # | Scenario | Expected Behavior | Handling | Affected Layers |
|---|----------|-------------------|----------|-----------------|
| 11.1 | Bank statement from a non-Indian bank (USD/EUR amounts) | Process amounts as-is; show as "₹" anyway (prototype limitation) — or detect currency and warn | Warn: "Non-INR currency detected; amounts shown without conversion" | Parser, Cleaner, Frontend |
| 11.2 | Statement has only balance enquiry transactions (no actual spend/income) | Metrics all zero; generate insight: "No spending data found in this statement" | Handle gracefully; empty metrics | Metrics, Insights |
| 11.3 | Statement from a bank format not in the parser's known formats | Best-effort parse; if >50% rows fail, mark statement as "failed" with suggestion to try CSV format | Adaptive parsing with failure threshold | Parser |
| 11.4 | User drags and drops multiple files at once | Accept only first file; show message "Only one file supported at a time" | Single-file validation on drop handler | `FileUpload.tsx` |
| 11.5 | Browser tab closed during processing | Backend continues processing; data available if user returns with same statement_id | Backend is independent of frontend state | Backend, Frontend |
| 11.6 | User's browser has JavaScript disabled | App won't render — this is an SPA; no SSR fallback in prototype | Prototype requires JS; documented limitation | Frontend |
