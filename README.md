# 💰 Rupee Radar

Rupee Radar is an AI-powered personal finance analytics platform that helps users understand their spending habits, identify recurring expenses, and generate actionable financial insights from bank statements.

## 🚀 Features

### 📊 Transaction Analysis

* Upload bank statements in CSV format
* Automatic transaction processing and categorization
* Clean and structured financial data

### 🤖 AI-Powered Insights

* Intelligent spending analysis
* Personalized financial recommendations
* Expense pattern detection
* Smart financial summaries

### 📈 Financial Dashboard

* Monthly spending overview
* Category-wise expense breakdown
* Top transactions analysis
* Financial health metrics

### 🔄 Recurring Expense Detection

* Identify subscriptions and recurring payments
* Track monthly commitments
* Monitor spending trends

### 📄 Report Generation

* Download financial reports
* Summary of spending behavior
* AI-generated recommendations

---

## 🛠️ Tech Stack

### Frontend

* React
* TypeScript
* Vite
* Tailwind CSS

### Backend

* Python
* FastAPI
* SQLAlchemy
* Alembic

### AI Integration

* Groq API
* LLM-based categorization
* AI-generated insights

### Database

* SQLite

### Deployment

* Docker
* Docker Compose

---

## 📂 Project Structure

```text
RupeeRadar/
├── backend/
│   ├── app/
│   ├── alembic/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
├── architecture.md
├── implementation-plan.md
└── README.md
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/vikhyathks-10/rupee-radar.git
cd rupee-radar
```

### Backend Setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend

npm install
npm run dev
```

---

## 🔐 Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=YOUR_GROQ_API_KEY
GROQ_MODEL=llama-3.3-70b-versatile
```

---

## ▶️ Run Application

### Backend

```bash
cd backend
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm run dev
```

---

## 📊 Sample Workflow

1. Upload bank statement CSV
2. Transactions are processed and categorized
3. Financial metrics are calculated
4. AI generates spending insights
5. User views dashboard and reports

---

## 🎯 Future Enhancements

* Multi-bank integration
* Budget planning
* Expense forecasting
* Investment tracking
* Mobile application
* Real-time notifications

---

## 👨‍💻 Author

**Vikhyath Bharadwaj K S**

B.Tech Computer Science & Engineering
PES University, Electronic City, Bengaluru

GitHub: https://github.com/vikhyathks-10

---

## 📜 License

This project is developed for educational and learning purposes.
