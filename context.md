# RupeeRadar — Project Context

## Project Overview

RupeeRadar is an AI-powered personal finance assistant that helps working professionals understand where their money is going by analyzing bank statement data. It transforms raw, messy financial transaction data into meaningful personal finance insights through an end-to-end workflow.

## Problem Statement

Working professionals make hundreds of monthly transactions across UPI, cards, bank transfers, subscriptions, EMIs, rent, shopping, food delivery, travel, and investments. Bank statements contain all this information, but transaction descriptions are messy, inconsistent, and hard to categorize manually. RupeeRadar solves this by automating the extraction, cleaning, categorization, and insight generation process.

## Key User Questions

The solution should help users answer:

- What are my biggest spending categories?
- How much did I spend this month?
- Which transactions are recurring subscriptions or EMIs?
- What was my biggest transaction?
- What are the top insights from my spending behavior?

## Core Requirements

1. **Data Input** — Accept bank statement data as input
2. **Transaction Cleaning** — Extract or clean transactions into a structured format
3. **Categorization** — Categorize transactions into meaningful groups:
   - Food, Travel, Shopping, Bills, EMI, Subscriptions, Salary, Rent, Investments, Other
4. **Recurring Detection** — Identify recurring transactions (subscriptions, EMIs, rent, SIPs, insurance)
5. **Financial Metrics** — Calculate total income, total spend, savings, top categories, biggest transactions
6. **Insight Generation** — Generate clear, human-readable spending insights using actual transaction amounts
7. **Output Presentation** — Present results through a simple UI, dashboard, or downloadable report

## Expected Deliverables

A working prototype demonstrating:

- Cleaned transaction data
- Categorized expenses
- Recurring payment detection
- Spend summary dashboard
- At least three personalized financial insights
- A final report or visual summary that can be shared

## Evaluation Criteria

- Accuracy of transaction cleaning and categorization
- Quality of financial insights
- Ability to handle real-world messy transaction descriptions
- Simplicity and usefulness of the user experience
- Completeness of the end-to-end workflow
- Privacy-conscious handling of sensitive financial data

## Constraints

- Prioritize a working end-to-end prototype over perfect support for every bank format
- Participants may choose their own technology stack and implementation approach

## Final Deliverable

A deployed or locally runnable application that takes raw bank statement data and produces a clear personal finance summary showing where the user's money is going.

## Architecture Decisions (Defined in architecture.md)

| Decision | Choice | Status |
|----------|---------|--------|
| Tech Stack | React + Vite (frontend) / Python + FastAPI (backend) | Decided |
| Frontend Framework | React 18 + Vite + Tailwind + shadcn/ui | Decided |
| Backend Framework | Python 3.11 + FastAPI + SQLAlchemy | Decided |
| Data Processing | Pandas for cleaning; pdfplumber + csv for parsing | Decided |
| AI/NLP for Categorization | OpenAI GPT-4o API (hybrid: rules + AI) | Decided |
| Deployment Strategy | Docker Compose (local); Railway/Render (cloud) | Decided |
| Input Format Support | CSV and PDF | Decided |
| Database | SQLite via SQLAlchemy | Decided |
| Charts & Visualization | Recharts | Decided |
| PDF Report Generation | ReportLab | Decided |

## Project Workspace

- **Root Directory:** `c:\Users\vikhy\OneDrive\Desktop\PROJECT-MSI\RUPEERADAR`
- **Problem Statement Source:** `problemStatement.txt`
