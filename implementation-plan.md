# RupeeRadar — Phase-Wise Implementation Plan

This plan breaks the RupeeRadar prototype into 6 phases, ordered by dependency. Each phase produces a verifiable milestone. Within each phase, tasks are ordered by critical path.

---

## Phase 1: Project Setup & Skeleton

**Goal:** Scaffold both frontend and backend, wire them together, and confirm the dev environment runs.

**Estimated Duration:** 1 day

### Tasks

| # | Task | Files / Commands | Verification |
|---|------|-------------------|--------------|
| 1.1 | Create backend project scaffold | `backend/requirements.txt`, `backend/pyproject.toml`, `backend/app/main.py`, `backend/app/config.py`, `backend/app/database.py` | `uvicorn app.main:app --reload` starts and `/docs` shows Swagger UI |
| 1.2 | Create frontend project scaffold | `npm create vite@latest frontend -- --template react-ts`, install Tailwind, shadcn/ui, React Router, Recharts, Zustand, Axios | `npm run dev` shows a blank app on `localhost:5173` |
| 1.3 | Create Docker Compose + .env.example | `docker-compose.yml`, `.env.example` | `docker compose up` starts both services |
| 1.4 | Create backend directory structure | Create all dirs under `backend/app/`: `models/`, `schemas/`, `api/`, `services/`, `ai/`, `utils/`, `tests/`, `data/` | Directory tree matches architecture.md section 3 |
| 1.5 | Create frontend directory structure | Create all dirs under `frontend/src/`: `api/`, `components/`, `pages/`, `hooks/`, `store/`, `lib/` | Directory tree matches architecture.md section 3 |
| 1.6 | Create initial data files | `backend/app/data/category_keywords.json`, `backend/app/data/recurring_merchants.json`, `backend/app/data/sample_statements/` (add 1 sample CSV) | JSON files loadable; sample CSV has 10-20 test transactions |
| 1.7 | Wire frontend API client to backend | `frontend/src/api/client.ts` (base URL = `localhost:8000/api`), `frontend/src/api/types.ts` (all response types from architecture.md section 5) | Frontend can `GET /api/health` and receive a response |

**Phase 1 Milestone:** Both services start, frontend reaches backend via API client, Docker Compose works.

---

## Phase 2: Backend Core — Data Pipeline (Parse → Clean → Categorize)

**Goal:** Build the three core processing services and the pipeline orchestrator. Upload a CSV, and get back cleaned, categorized transactions from the API.

**Estimated Duration:** 2-3 days

### Tasks

| # | Task | Files | Verification |
|---|------|------|--------------|
| 2.1 | Define ORM models | `backend/app/models/statement.py`, `backend/app/models/transaction.py`, `backend/app/models/insight.py` | SQLAlchemy creates all 3 tables on startup |
| 2.2 | Define Pydantic schemas | `backend/app/schemas/statement.py`, `backend/app/schemas/transaction.py`, `backend/app/schemas/insight.py`, `backend/app/schemas/metrics.py` | Schemas validate sample JSON payloads from architecture.md section 5 |
| 2.3 | Build CSV parser service | `backend/app/services/parser.py` — parse CSV bank statements into raw row dicts | Unit test: sample CSV → list of `{date, description, amount, type}` dicts |
| 2.4 | Build PDF parser service | Extend `parser.py` with pdfplumber-based PDF extraction | Unit test: sample PDF → same row dict format (or skip PDF if no sample available) |
| 2.5 | Build cleaner service | `backend/app/services/cleaner.py` — normalize dates, amounts, descriptions, deduplicate | Unit test: raw rows → cleaned rows with ISO dates, signed amounts, stripped descriptions |
| 2.6 | Build utility helpers | `backend/app/utils/date_utils.py`, `backend/app/utils/currency_utils.py`, `backend/app/utils/text_utils.py` | Unit tests for each utility pass |
| 2.7 | Build rule-based categorizer | `backend/app/services/categorizer.py` — first pass using `category_keywords.json` keyword matching | Unit test: "UPI/SWIGGY/..." → Food, "EMI-HDFC" → EMI, etc. |
| 2.8 | Build AI categorizer (OpenAI) | `backend/app/ai/openai_client.py`, `backend/app/ai/prompts.py`, `backend/app/ai/categorize_chain.py` — second pass for uncategorized items | Unit test with mock: uncategorized description → category label + confidence |
| 2.9 | Build hybrid categorizer integration | Wire rule-based + AI passes in `categorizer.py`; cache AI results by normalized description | Integration test: 20 transactions → all categorized, ~60% rules, ~40% AI |
| 2.10 | Build PII scrubber | Add scrubbing logic in `text_utils.py` or `categorizer.py` — remove account numbers, names, phone numbers before AI calls | Unit test: "UPI/SWIGGY/9876543210/John Doe" → "UPI/SWIGGY/..." (PII removed) |
| 2.11 | Build processing pipeline orchestrator | `backend/app/services/processing_pipeline.py` — chains parse → clean → categorize → save | Integration test: upload sample CSV → DB has cleaned + categorized transactions |

**Phase 2 Milestone:** `POST /api/upload` with a CSV returns `statement_id`, and `GET /api/transactions?statement_id=X` returns cleaned, categorized transactions.

---

## Phase 3: Backend Core — Recurring, Metrics, Insights, Report

**Goal:** Complete the remaining three pipeline stages and the PDF report generator. All 7 API endpoints return real data.

**Estimated Duration:** 2-3 days

### Tasks

| # | Task | Files | Verification |
|---|------|------|--------------|
| 3.1 | Build recurring detector | `backend/app/services/recurring_detector.py`, `backend/app/utils/recurring_rules.py` — group by merchant, check date intervals + amount consistency | Unit test: 3 Netflix transactions on same day monthly → flagged recurring with frequency "monthly" |
| 3.2 | Build metrics calculator | `backend/app/services/metrics_calculator.py` — compute income, spend, savings, savings rate, top categories, biggest transactions, monthly breakdown | Unit test: known transaction set → exact metrics values |
| 3.3 | Build AI insight generator | `backend/app/ai/insight_chain.py`, `backend/app/services/insight_generator.py` — send metrics payload to OpenAI, get 3-5 structured insights | Unit test with mock: metrics payload → 3 insight objects with title, description, severity |
| 3.4 | Integrate recurring + metrics + insights into pipeline | Extend `processing_pipeline.py` to call recurring_detector, metrics_calculator, insight_generator after categorization | Integration test: full pipeline on sample CSV → recurring items, metrics, and insights in DB |
| 3.5 | Build all GET API endpoints | `backend/app/api/router.py`, `transactions.py`, `categories.py`, `recurring.py`, `metrics.py`, `insights.py` | Each endpoint returns correct data for a processed statement |
| 3.6 | Build PDF report generator | `backend/app/services/report_generator.py` — ReportLab-based PDF with metrics, category breakdown, recurring list, insights | Unit test: generate PDF from sample data → valid PDF file with expected sections |
| 3.7 | Build report API endpoint | `backend/app/api/report.py` — `GET /api/report/pdf?statement_id=X` returns PDF binary | Browser can download and open the PDF |
| 3.8 | Add error handling & edge cases | Implement error handling from architecture.md section 11 — unsupported format, empty statement, AI fallback, DB rollback | Tests for each error scenario pass |
| 3.9 | Add upload endpoint with async processing | `backend/app/api/upload.py` — accept file, save to disk, trigger pipeline, return statement_id | `POST /api/upload` with CSV → returns `{ statement_id, status: "processing" }`; poll `GET /api/transactions` until status = "completed" |

**Phase 3 Milestone:** All 7 API endpoints functional. Upload a CSV → get transactions, categories, recurring, metrics, insights, and downloadable PDF report.

---

## Phase 4: Frontend — Upload & Dashboard UI

**Goal:** Build the complete frontend UI: upload flow, dashboard with charts, insights page, and report download.

**Estimated Duration:** 2-3 days

### Tasks

| # | Task | Files | Verification |
|---|------|------|--------------|
| 4.1 | Build Zustand store | `frontend/src/store/transactionStore.ts` — statement_id, processing status, transactions, categories, metrics, insights, recurring, actions | Store initializes with idle state; actions are callable |
| 4.2 | Build Layout component | `frontend/src/components/Layout.tsx` — sidebar navigation + header + main content area | Layout renders on all routes |
| 4.3 | Build React Router setup | `frontend/src/App.tsx` — routes: `/` (Upload), `/dashboard`, `/insights`, `/report` | Navigation between pages works |
| 4.4 | Build utility helpers | `frontend/src/lib/formatCurrency.ts` (INR formatter), `frontend/src/lib/formatDate.ts` | `formatCurrency(450)` → "₹450" |
| 4.5 | Build Upload page + component | `frontend/src/pages/UploadPage.tsx`, `frontend/src/components/FileUpload.tsx` — drag-drop file input, progress indicator, processing status | Upload a CSV → processing completes → auto-navigates to dashboard |
| 4.6 | Build useUpload hook | `frontend/src/hooks/useUpload.ts` — manage upload state, call API, poll for completion | Hook returns { status, uploadFile, statementId } |
| 4.7 | Build Dashboard page | `frontend/src/pages/DashboardPage.tsx` — container for all dashboard widgets | Dashboard renders after upload |
| 4.8 | Build MetricsSummary component | `frontend/src/components/MetricsSummary.tsx` — 3 cards: Total Income, Total Spend, Savings (with savings rate) | Cards display correct values from API |
| 4.9 | Build CategoryPieChart component | `frontend/src/components/CategoryPieChart.tsx` — Recharts PieChart of category breakdown | Pie chart renders with category data |
| 4.10 | Build MonthlyBarChart component | `frontend/src/components/MonthlyBarChart.tsx` — Recharts BarChart of monthly income vs spend | Bar chart renders with monthly data |
| 4.11 | Build TopTransactions component | `frontend/src/components/TopTransactions.tsx` — table of top 5 biggest debit transactions | Table displays biggest transactions |
| 4.12 | Build RecurringList component | `frontend/src/components/RecurringList.tsx` — table of detected recurring payments with frequency & annual cost | Table displays recurring items |
| 4.13 | Build useTransactions + useInsights hooks | `frontend/src/hooks/useTransactions.ts`, `frontend/src/hooks/useInsights.ts` | Hooks fetch and return data from respective APIs |

**Phase 4 Milestone:** Full upload-to-dashboard flow works. Upload CSV → see metrics cards, pie chart, bar chart, top transactions, recurring list.

---

## Phase 5: Frontend — Insights & Report Pages + Polish

**Goal:** Complete the Insights and Report pages, add loading states, error handling, and UI polish.

**Estimated Duration:** 1-2 days

### Tasks

| # | Task | Files | Verification |
|---|------|------|--------------|
| 5.1 | Build InsightCards component | `frontend/src/components/InsightCards.tsx` — display AI insights as styled cards with severity badges (info/warning/critical) | Insight cards render with title, description, severity color |
| 5.2 | Build Insights page | `frontend/src/pages/InsightsPage.tsx` — full-page view of all generated insights | Page shows all insights after processing |
| 5.3 | Build ReportPreview component | `frontend/src/components/ReportPreview.tsx` — embedded HTML preview of report content (metrics + categories + insights) | Preview renders structured report content |
| 5.4 | Build ReportDownload component | `frontend/src/components/ReportDownload.tsx` — button to download PDF from `GET /api/report/pdf` | Click → downloads PDF file |
| 5.5 | Build Report page | `frontend/src/pages/ReportPage.tsx` — preview + download | Page shows preview and download button |
| 5.6 | Add loading skeletons | Add loading/spinner states to all data-dependent components (charts, tables, cards) | Loading states appear while data is fetching |
| 5.7 | Add error handling UI | Error banners for: upload failure, processing failure, empty results, API errors | Error states display helpful messages |
| 5.8 | Add empty state UI | "No data yet — upload a statement" when no statement_id is active | Empty state renders on dashboard before upload |
| 5.9 | Polish responsive layout | Ensure dashboard works on tablet/mobile widths; adjust chart sizes | Dashboard is usable at 768px width |
| 5.10 | Add processing progress indicator | Show step-by-step progress (Parsing → Cleaning → Categorizing → Detecting Recurring → Computing Metrics → Generating Insights) on upload page | Progress bar updates during processing |

**Phase 5 Milestone:** All 4 pages (Upload, Dashboard, Insights, Report) are complete with loading states, error handling, and responsive design.

---

## Phase 6: Testing, Dockerization & Final Delivery

**Goal:** Write backend + frontend tests, finalize Docker setup, and produce a runnable deliverable.

**Estimated Duration:** 1-2 days

### Tasks

| # | Task | Files / Commands | Verification |
|---|------|-------------------|--------------|
| 6.1 | Write backend parser tests | `backend/app/tests/test_parser.py` — CSV and PDF extraction with sample statements | `pytest test_parser.py` passes |
| 6.2 | Write backend cleaner tests | `backend/app/tests/test_cleaner.py` — date normalization, amount parsing, dedup, noise removal | `pytest test_cleaner.py` passes |
| 6.3 | Write backend categorizer tests | `backend/app/tests/test_categorizer.py` — rule-based coverage, AI mock, hybrid integration | `pytest test_categorizer.py` passes |
| 6.4 | Write backend recurring tests | `backend/app/tests/test_recurring.py` — date clustering, amount consistency, frequency detection | `pytest test_recurring.py` passes |
| 6.5 | Write backend metrics tests | `backend/app/tests/test_metrics.py` — exact calculations with known data | `pytest test_metrics.py` passes |
| 6.6 | Write backend API integration tests | `backend/app/tests/test_api.py` — full upload → fetch results flow | `pytest test_api.py` passes |
| 6.7 | Write frontend component tests | Vitest tests for key components (FileUpload, MetricsSummary, CategoryPieChart) | `npm run test` passes |
| 6.8 | Finalize Docker setup | `frontend/Dockerfile`, `backend/Dockerfile`, `docker-compose.yml` — production-ready builds | `docker compose up --build` → both services start, app works end-to-end |
| 6.9 | Create README with run instructions | `README.md` — local run (Docker), local dev (separate terminals), env setup, sample data | A new user can follow README to run the app |
| 6.10 | End-to-end smoke test | Run full flow: upload sample CSV → verify dashboard, insights, PDF download | All features work without errors |

**Phase 6 Milestone:** All tests pass, Docker Compose runs the full app, end-to-end flow is verified, deliverable is ready.

---

## Dependency Graph

```
Phase 1 (Setup)
    │
    ▼
Phase 2 (Pipeline: Parse → Clean → Categorize)
    │
    ▼
Phase 3 (Pipeline: Recurring → Metrics → Insights → Report)
    │
    ├──────────────────────────┐
    ▼                          ▼
Phase 4 (Frontend: Upload + Dashboard)   ← can start API integration once Phase 3 endpoints exist
    │
    ▼
Phase 5 (Frontend: Insights + Report + Polish)
    │
    ▼
Phase 6 (Testing + Dockerization + Delivery)
```

**Note:** Phase 4 frontend scaffolding (4.1–4.4) can begin in parallel with Phase 3, but API-dependent components (4.5–4.13) require Phase 3 endpoints.

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| OpenAI API key unavailable | Build rule-only fallback; test with mocks; AI is additive, not required for MVP |
| PDF parsing fails on real bank statements | Start with CSV-only support; add PDF in Phase 2 task 2.4 as stretch goal |
| Sample bank statements unavailable | Generate synthetic test data matching typical Indian bank formats |
| Frontend-backend integration delays | Use mocked API responses during Phase 4 development; swap to real API in Phase 5 |
| Docker build issues on Windows | Test Docker Compose early (Phase 1 task 1.3); fallback to manual `uvicorn` + `npm run dev` |

---

## Quick-Start Sequence (After All Phases Complete)

```bash
# 1. Clone & enter project
cd RUPEERADAR

# 2. Copy env file and add OpenAI key
cp .env.example .env
# Edit .env → add OPENAI_API_KEY

# 3. Start with Docker
docker compose up --build

# 4. Open browser
# Frontend: http://localhost:5173
# Backend API docs: http://localhost:8000/docs

# 5. Upload a bank statement CSV → view dashboard → download report
```
