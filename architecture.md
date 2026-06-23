# RupeeRadar — Architecture Design

## 1. System Architecture Overview

RupeeRadar follows a **client-server architecture** with a React frontend and a Python FastAPI backend. The backend handles all data processing, AI-powered categorization, and insight generation, while the frontend provides an interactive dashboard for users to upload statements and visualize results.

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React + Vite)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Upload   │  │ Dashboard│  │ Insights │  │  Report   │   │
│  │   Page    │  │   Page   │  │   Page   │  │   Page    │   │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘   │
│        │             │             │             │          │
│        └─────────────┴─────────────┴─────────────┘          │
│                        │ REST API Calls                     │
└────────────────────────┼────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (Python + FastAPI)                 │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    API Layer                          │   │
│  │  Upload │ Process │ Categorize │ Recurring │ Insights│   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                   │
│  ┌──────────────────────┴───────────────────────────────┐   │
│  │              Processing Pipeline                      │   │
│  │                                                       │   │
│  │  ┌─────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │  │ Parser  │→│  Cleaner  │→│Categorizer│            │   │
│  │  │ Module  │  │  Module   │  │  Module  │            │   │
│  │  └─────────┘  └──────────┘  └──────────┘            │   │
│  │       │             │             │                   │   │
│  │       ▼             ▼             ▼                   │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │ Recurring │  │ Metrics  │  │ Insights │           │   │
│  │  │ Detector  │  │ Computer │  │Generator │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────┐  ┌────────────────┐                    │
│  │  SQLite DB     │  │  File Storage   │                    │
│  │  (Transactions)│  │  (Statements)   │                    │
│  └────────────────┘  └────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | React 18 + Vite | Fast dev server, modern SPA, rich chart ecosystem |
| **UI Framework** | Tailwind CSS + shadcn/ui | Utility-first styling, accessible components |
| **Charts** | Recharts | React-native charting, supports pie/bar/line/area |
| **Backend** | Python 3.11 + FastAPI | Async support, auto OpenAPI docs, lightweight |
| **Data Processing** | Pandas | Industry standard for tabular data cleaning |
| **AI Categorization** | OpenAI GPT-4o API | High accuracy on messy transaction descriptions |
| **Recurring Detection** | Custom algorithm + date clustering | Detect periodic payments without external dependency |
| **Insight Generation** | OpenAI GPT-4o API | Natural language insights from computed metrics |
| **Database** | SQLite (via SQLAlchemy) | Zero-setup, file-based, sufficient for prototype |
| **File Parsing** | pdfplumber + csv stdlib | PDF and CSV bank statement extraction |
| **PDF Report** | ReportLab | Generate downloadable PDF summaries |
| **Validation** | Pydantic | Strict schema validation for API contracts |
| **Testing** | pytest + Vitest | Backend and frontend test runners |
| **Deployment** | Docker Compose | Single-command local run; optional cloud deploy |

---

## 3. Directory Structure

```
RUPEERADAR/
├── context.md
├── architecture.md
├── problemStatement.txt
├── docker-compose.yml
├── .env.example
│
├── frontend/                         # React + Vite SPA
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── index.html
│   ├── public/
│   │   └── favicon.ico
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── index.css                 # Tailwind base styles
│       ├── api/
│       │   └ client.ts              # Axios/fetch wrapper with base URL
│       │   └ types.ts               # API response type definitions
│       ├── components/
│       │   ├── ui/                   # shadcn/ui primitives
│       │   ├── FileUpload.tsx        # Drag-and-drop CSV/PDF upload
│       │   ├── Dashboard.tsx         # Main spending dashboard
│       │   ├── CategoryPieChart.tsx  # Pie chart of spending categories
│       │   ├── MonthlyBarChart.tsx   # Monthly income vs spend bars
│       │   ├── TopTransactions.tsx   # Table of biggest transactions
│       │   ├── RecurringList.tsx     # Recurring payments table
│       │   ├── InsightCards.tsx      # AI-generated insight cards
│       │   ├── MetricsSummary.tsx    # Income/spend/savings totals
│       │   ├── ReportDownload.tsx    # PDF report download button
│       │   └ Layout.tsx             # Sidebar + header layout
│       ├── pages/
│       │   ├── UploadPage.tsx        # Statement upload flow
│       │   ├── DashboardPage.tsx     # Main dashboard view
│       │   ├── InsightsPage.tsx      # Detailed insights view
│       │   └ ReportPage.tsx         # Report preview & download
│       ├── hooks/
│       │   ├── useUpload.ts          # Upload + processing state hook
│       │   ├── useTransactions.ts    # Fetch cleaned transactions
│       │   ├── useInsights.ts        # Fetch AI insights
│       ├── store/
│       │   └ transactionStore.ts    # Zustand store for transaction state
│       └── lib/
│           ├── formatCurrency.ts     # INR currency formatter
│           ├── formatDate.ts         # Date display helpers
│
├── backend/                          # Python FastAPI server
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── alembic.ini                   # DB migration config
│   ├── alembic/
│   │   └ migrations/
│   ├── app/
│   │   ├── main.py                   # FastAPI app entry point
│   │   ├── config.py                 # Settings from .env
│   │   ├── database.py               # SQLAlchemy engine + session
│   │   ├── models/
│   │   │   ├── transaction.py        # Transaction ORM model
│   │   │   ├── statement.py          # Statement ORM model (metadata)
│   │   │   ├── insight.py            # Insight ORM model
│   │   ├── schemas/
│   │   │   ├── transaction.py        # Pydantic request/response schemas
│   │   │   ├── statement.py          # Upload & statement schemas
│   │   │   ├── insight.py            # Insight response schemas
│   │   │   ├── metrics.py            # Financial metrics schemas
│   │   ├── api/
│   │   │   ├── router.py             # Root router aggregation
│   │   │   ├── upload.py             # POST /upload endpoint
│   │   │   ├── transactions.py       # GET /transactions endpoints
│   │   │   ├── categories.py         # GET /categories breakdown
│   │   │   ├── recurring.py          # GET /recurring endpoint
│   │   │   ├── metrics.py            # GET /metrics endpoint
│   │   │   ├── insights.py           # GET /insights endpoint
│   │   │   ├── report.py             # GET /report/pdf endpoint
│   │   ├── services/
│   │   │   ├── parser.py             # CSV/PDF statement parser
│   │   │   ├── cleaner.py            # Transaction cleaning service
│   │   │   ├── categorizer.py        # AI + rule-based categorization
│   │   │   ├── recurring_detector.py # Recurring payment detection
│   │   │   ├── metrics_calculator.py # Financial metrics computation
│   │   │   ├── insight_generator.py  # AI insight generation
│   │   │   ├── report_generator.py   # PDF report builder
│   │   │   ├── processing_pipeline.py # Orchestrates full pipeline
│   │   ├── ai/
│   │   │   ├── openai_client.py      # OpenAI API wrapper
│   │   │   ├── prompts.py            # Categorization & insight prompts
│   │   │   ├── categorize_chain.py   # Structured categorization chain
│   │   │   ├── insight_chain.py      # Insight generation chain
│   │   ├── utils/
│   │   │   ├── date_utils.py         # Date parsing & normalization
│   │   │   ├── currency_utils.py     # INR amount parsing
│   │   │   ├── text_utils.py         # Description cleaning helpers
│   │   │   ├── recurring_rules.py    # Merchant name matching rules
│   │   ├── tests/
│   │   │   ├── test_parser.py
│   │   │   ├── test_cleaner.py
│   │   │   ├── test_categorizer.py
│   │   │   ├── test_recurring.py
│   │   │   ├── test_metrics.py
│   │   │   ├── test_api.py
│   │   └── data/
│   │       ├── sample_statements/    # Sample bank statements for testing
│   │       ├── category_keywords.json # Rule-based keyword mapping
│   │       ├── recurring_merchants.json # Known recurring merchant list
│
└── shared/
    └── types.ts                      # Shared type definitions (if needed)
```

---

## 4. Data Flow

The end-to-end processing pipeline flows through six stages:

```
User Upload → Parse → Clean → Categorize → Detect Recurring → Compute Metrics → Generate Insights
```

### Stage 1: Parse (Upload & Extraction)
- User uploads a bank statement (CSV or PDF) via the frontend
- The file is sent to `POST /api/upload`
- The parser module extracts raw transaction rows from the file
- Each row contains: date, description, amount, type (debit/credit)

### Stage 2: Clean (Normalization)
- Dates are parsed into ISO 8601 format (`YYYY-MM-DD`)
- Amounts are normalized to signed floats (negative for debits, positive for credits)
- Descriptions are stripped of noise (bank codes, transaction IDs, extra whitespace)
- Duplicate transactions are removed
- Rows with missing critical fields are flagged or dropped

### Stage 3: Categorize (AI + Rules)
- **Rule-based first pass:** Known keywords mapped to categories via `category_keywords.json`
  - Example: "SWIGGY" → Food, "AMAZON" → Shopping, "EMI-" → EMI
- **AI second pass:** Uncategorized transactions are sent to OpenAI with the description and amount
  - The AI returns a category label from the defined set
  - Results are cached to reduce API calls for similar descriptions

### Stage 4: Detect Recurring
- Transactions are grouped by normalized merchant name
- Date intervals are analyzed for periodicity (monthly, quarterly, annual)
- Amount consistency is checked (same or similar amounts across occurrences)
- Transactions matching known recurring merchants are flagged automatically
- Output: list of recurring items with frequency, next expected date, and total annual cost

### Stage 5: Compute Metrics
- **Total Income:** Sum of all credit (positive) transactions
- **Total Spend:** Sum of all debit (negative) transactions
- **Savings:** Total Income - Total Spend
- **Savings Rate:** Savings / Total Income (percentage)
- **Top Categories:** Spending ranked by category total
- **Biggest Transactions:** Top 5 largest debit transactions
- **Monthly Breakdown:** Income and spend grouped by month

### Stage 6: Generate Insights
- Computed metrics and categorized data are sent to OpenAI
- The AI is prompted to produce 3–5 personalized, human-readable insights
- Each insight references specific amounts and categories
- Example: "You spend 38% of your income on Food — that's ₹12,400/month, above the recommended 25%"

---

## 5. API Design

### Base URL: `/api`

| Endpoint | Method | Description | Request | Response |
|----------|--------|-------------|---------|----------|
| `/upload` | POST | Upload & process a bank statement | FormData: file (CSV/PDF) | `{ statement_id, status, transaction_count }` |
| `/transactions` | GET | List all cleaned transactions | `?statement_id=&category=&page=&limit=` | `{ transactions: Transaction[], total }` |
| `/categories` | GET | Get spending breakdown by category | `?statement_id=` | `{ categories: { name, total, count, percentage }[] }` |
| `/recurring` | GET | List detected recurring payments | `?statement_id=` | `{ recurring: RecurringItem[] }` |
| `/metrics` | GET | Get computed financial metrics | `?statement_id=` | `{ MetricsResponse }` |
| `/insights` | GET | Get AI-generated insights | `?statement_id=` | `{ insights: Insight[] }` |
| `/report/pdf` | GET | Download PDF report | `?statement_id=` | PDF binary stream |

### Key Response Schemas

**Transaction:**
```json
{
  "id": "uuid",
  "date": "2025-01-15",
  "description": "Swiggy Order #12345",
  "original_description": "UPI/SWIGGY/123456789/ORDER12345",
  "amount": -450.00,
  "category": "Food",
  "is_recurring": false,
  "cleaned": true
}
```

**MetricsResponse:**
```json
{
  "total_income": 85000.00,
  "total_spend": 62000.00,
  "savings": 23000.00,
  "savings_rate": 27.06,
  "top_categories": [
    { "name": "Food", "total": 12400.00, "percentage": 20.0 },
    { "name": "Shopping", "total": 8000.00, "percentage": 12.9 }
  ],
  "biggest_transactions": [
    { "description": "Rent Payment", "amount": -15000.00, "date": "2025-01-01" }
  ],
  "monthly_breakdown": [
    { "month": "2025-01", "income": 85000.00, "spend": 62000.00 }
  ]
}
```

**RecurringItem:**
```json
{
  "merchant": "Netflix Subscription",
  "amount": -499.00,
  "frequency": "monthly",
  "occurrences": 3,
  "next_expected_date": "2025-04-15",
  "annual_cost": 5988.00,
  "category": "Subscriptions"
}
```

**Insight:**
```json
{
  "id": "uuid",
  "title": "High Food Spending",
  "description": "You spend 38% of your income on Food...",
  "severity": "warning",
  "category": "Food",
  "amount_referenced": 12400.00
}
```

---

## 6. Database Schema

SQLite with SQLAlchemy ORM. Three core tables:

### `statements`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Unique statement identifier |
| filename | String | Original uploaded filename |
| file_type | String | "csv" or "pdf" |
| upload_date | DateTime | When the statement was uploaded |
| transaction_count | Integer | Number of transactions extracted |
| status | String | "processing", "completed", "failed" |
| processing_error | String (nullable) | Error message if processing failed |

### `transactions`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Unique transaction identifier |
| statement_id | UUID (FK) | Links to parent statement |
| date | Date | Normalized transaction date |
| description | String | Cleaned transaction description |
| original_description | String | Raw description from bank statement |
| amount | Float | Signed amount (+credit, -debit) |
| category | String | Assigned category label |
| is_recurring | Boolean | Flagged as recurring payment |
| recurring_group_id | UUID (nullable) | Links to recurring payment group |
| confidence | Float (nullable) | AI categorization confidence score |

### `insights`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Unique insight identifier |
| statement_id | UUID (FK) | Links to parent statement |
| title | String | Insight headline |
| description | String | Full insight description |
| severity | String | "info", "warning", "critical" |
| category | String (nullable) | Related spending category |
| amount_referenced | Float (nullable) | Specific amount mentioned |
| created_at | DateTime | When insight was generated |

---

## 7. Frontend Architecture

### Routing (React Router v6)

| Route | Page Component | Description |
|-------|---------------|-------------|
| `/` | `UploadPage` | Upload a bank statement |
| `/dashboard` | `DashboardPage` | Main spending dashboard |
| `/insights` | `InsightsPage` | Detailed AI insights |
| `/report` | `ReportPage` | Report preview & PDF download |

### State Management (Zustand)

Single store `transactionStore` manages:
- Current `statement_id` (active session)
- Processing status (idle / uploading / processing / completed / error)
- Transaction data, categories, metrics, insights, recurring items
- Actions: `uploadFile`, `fetchTransactions`, `fetchInsights`, etc.

### Component Hierarchy

```
App
├── Layout
│   ├── Sidebar (navigation)
│   ├── Header (statement info, status indicator)
│   └── Main Content (route-based)
│       ├── UploadPage
│       │   └ FileUpload (drag-drop, progress bar)
│       ├── DashboardPage
│       │   ├── MetricsSummary (income/spend/savings cards)
│       │   ├── CategoryPieChart (spending distribution)
│       │   ├── MonthlyBarChart (income vs spend timeline)
│       │   ├── TopTransactions (biggest debits table)
│       │   ├── RecurringList (recurring payments table)
│       │   └ ReportDownload (PDF download trigger)
│       ├── InsightsPage
│       │   └ InsightCards (AI-generated insight cards)
│       ├── ReportPage
│       │   └ ReportPreview (embedded PDF or HTML preview)
│       │   └ ReportDownload (PDF download button)
```

---

## 8. Backend Architecture

### Processing Pipeline (Service Layer)

The `ProcessingPipeline` service orchestrates the full flow after upload:

```python
async def process_statement(statement_id: str, file_path: str):
    # 1. Parse raw transactions from file
    raw_txns = parser.parse(file_path, file_type)

    # 2. Clean and normalize transactions
    cleaned_txns = cleaner.clean(raw_txns)

    # 3. Categorize using rules + AI
    categorized_txns = categorizer.categorize(cleaned_txns)

    # 4. Detect recurring payments
    recurring_map = recurring_detector.detect(categorized_txns)
    # Mark recurring transactions

    # 5. Compute financial metrics
    metrics = metrics_calculator.compute(categorized_txns)

    # 6. Generate AI insights
    insights = insight_generator.generate(categorized_txns, metrics)

    # 7. Save all results to database
    save_transactions(categorized_txns)
    save_insights(insights)
    update_statement_status(statement_id, "completed")
```

### Categorization Strategy (Hybrid: Rules + AI)

**Layer 1 — Rule-Based (Fast, Zero Cost):**
- Keyword dictionary: `category_keywords.json` maps merchant tokens to categories
- Pattern matching: regex for EMI patterns (`EMI-.*`), UPI identifiers (`UPI/.*`)
- Covers ~60-70% of common Indian transaction descriptions

**Layer 2 — AI-Powered (High Accuracy):**
- Remaining uncategorized transactions are batched and sent to OpenAI
- Prompt includes: transaction description, amount, and the 10 defined categories
- Response is structured JSON with category label and confidence score
- Results are cached by normalized description to avoid re-calling for similar items

### Recurring Detection Algorithm

```
1. Group transactions by normalized_merchant_name
2. For each group with ≥ 2 occurrences:
   a. Sort by date
   b. Compute intervals between consecutive dates
   c. Check if intervals are consistent (±5 days tolerance)
   d. Check if amounts are consistent (±10% tolerance)
   e. If both consistent → flag as recurring
   f. Determine frequency: monthly (~30d), quarterly (~90d), annual (~365d)
3. Cross-reference with known recurring merchants (Netflix, Spotify, etc.)
4. Calculate annual projected cost = amount × (12 / frequency_in_months)
```

### Insight Generation Prompt Strategy

The AI receives a structured payload containing:
- Top 5 spending categories with totals
- Monthly income/spend/savings
- Recurring payments list
- Biggest transactions
- Savings rate

The prompt instructs the AI to:
1. Generate 3-5 specific, actionable insights
2. Reference exact amounts in INR
3. Assign severity (info / warning / critical)
4. Suggest concrete actions where possible
5. Avoid generic advice; focus on the user's actual data

---

## 9. Security & Privacy

### Data Handling Principles

| Principle | Implementation |
|-----------|---------------|
| **No persistent raw data** | Original bank statement files deleted after parsing |
| **Local-first storage** | SQLite file stored locally, never transmitted externally |
| **Minimal AI payload** | Only descriptions sent to OpenAI; no account numbers, names, or IDs |
| **No user authentication** | Prototype mode — single-session, no persistent user accounts |
| **No cloud storage** | All data stays on the user's machine; Docker volume for local run |
| **AI data scrubbing** | Descriptions stripped of PII before sending to OpenAI API |

### PII Scrubbing Before AI Calls

Before any transaction description is sent to OpenAI:
- Remove account numbers, card numbers, phone numbers
- Remove personal names (replace with "USER")
- Remove addresses and Aadhaar/PAN references
- Keep only merchant name and transaction type for categorization

---

## 10. Deployment Architecture

### Local Development (Docker Compose)

```yaml
# docker-compose.yml
services:
  frontend:
    build: ./frontend
    ports: ["5173:5173"]
    volumes: ["./frontend:/app"]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    volumes:
      - ./backend:/app
      - data-volume:/app/data
    env_file: .env

  data-volume:  # Persistent SQLite + uploaded files
```

### Environment Variables (.env.example)

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# Application
APP_ENV=development
UPLOAD_DIR=./data/uploads
DB_PATH=./data/rupeeradar.db

# Server
BACKEND_PORT=8000
FRONTEND_PORT=5173
```

### Production Deployment Options

| Option | Strategy | Notes |
|--------|----------|-------|
| **Vercel (frontend)** | Static SPA deploy | Frontend only; backend needs separate hosting |
| **Railway / Render (backend)** | Docker deploy | Easiest full-stack cloud deployment |
| **Self-hosted** | Docker Compose on VPS | Full control, data stays on user's server |

---

## 11. Error Handling Strategy

| Scenario | Handling |
|----------|----------|
| Unsupported file format | Return 400 with supported formats list (CSV, PDF) |
| Corrupted/unreadable file | Return 422 with parsing error details |
| OpenAI API failure | Fall back to rule-only categorization; log error |
| OpenAI rate limit | Batch with delays; retry with exponential backoff |
| Empty statement (0 transactions) | Return 200 with empty results; warn user |
| Database write failure | Transaction rollback; mark statement as "failed" |
| Missing fields in transaction | Skip row with warning log; continue processing |

---

## 12. Testing Strategy

### Backend Tests (pytest)
- **Parser tests:** Validate CSV and PDF extraction with sample statements
- **Cleaner tests:** Verify date normalization, amount parsing, deduplication
- **Categorizer tests:** Rule-based coverage + AI mock responses
- **Recurring tests:** Known recurring patterns and edge cases
- **Metrics tests:** Calculation accuracy with known datasets
- **API tests:** End-to-end upload → process → fetch results

### Frontend Tests (Vitest)
- **Component tests:** Render each page component with mock data
- **Hook tests:** Verify data fetching and state transitions
- **Integration:** Upload → dashboard flow with mock API

---

## 13. Performance Considerations

| Concern | Mitigation |
|---------|------------|
| Large statements (>1000 rows) | Paginated API responses; streaming PDF report |
| OpenAI API latency | Process uncategorized in batches of 20; show progress |
| OpenAI API cost | Rule-based first pass reduces AI calls to ~30-40% of total |
| Dashboard render speed | Memoized charts; lazy-loaded pages |
| PDF generation time | Pre-generate on processing completion; cache result |

---

## 14. Future Enhancements (Post-Prototype)

- Multi-bank format support (HDFC, SBI, ICICI specific parsers)
- User authentication and multi-session support
- Historical trend analysis across multiple statement uploads
- Budget setting and overspend alerts
- WhatsApp/email report delivery
- Offline categorization with a fine-tuned local model
- Anomaly detection for unusual spending spikes
