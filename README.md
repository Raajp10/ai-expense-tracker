# AI Expense Tracker with RAG-Enhanced Financial Reasoning

Course: Database Systems (Final Project)  
Student: Raaj Patel  
Instructor: Prof. Shafkat Islam  
Semester: Fall 2025

This project implements a **full-stack AI expense tracker** that combines:

- A **SQLite** relational database for transactions, categories, and budgets
- A **FastAPI** backend for CRUD operations, analytics, and a small RAG (Retrieval-Augmented Generation) layer
- A **Next.js frontend** (run with `pnpm`) for charts, tables, and chat-style interaction
- A **local LLM** served via **Ollama** to generate natural-language financial explanations grounded in SQL results

The goal is to build a **privacy-preserving financial copilot** that can answer questions such as:

- “Why was my spending high last weekend?”
- “Which category pushed me over budget in December?”
- “How much did I spend on food this month compared to last month?”

All numerical values in answers are **strictly fetched from SQLite**; the LLM is only used for explanation.

---

## 1. Project Structure

```text
Ai-Expese-Tracker/
├── Backend/
│   ├── main.py
│   ├── models/          
│   ├── schemas/        
│   ├── db/              
│   ├── services/        
│   ├── routers/         
│   ├── data/           
│   ├── requirements.txt
│   └── .env.example
└── Frontend/
    ├── package.json
    ├── pnpm-lock.yaml
    ├── next.config.mjs / next.config.js
    ├── src/
    │   ├── pages/ or app/
    │   ├── components/
    │   └── lib/
    └── README.md (optional)
```

## 2. Key Features

- Natural-language queries over spending data
- RAG pipeline that converts questions → SQL → retrieved context → grounded answer
- Local-only processing (SQLite + FastAPI + Ollama on your machine)
- Budget vs Actual comparisons per category
- Simple anomaly detection (high-spend days and categories)
- Interactive dashboard built with Next.js (run using pnpm)

## 3. Technologies

### Backend
- Python 3.11
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic v2
- SQLite
- Ollama

### Frontend
- Node.js 18+
- Next.js
- React
- pnpm
- Recharts / D3.js

## 4. Backend Setup

All backend commands are run from the Backend/ directory.

### 4.1 Virtual Environment

```bash
cd Backend
python3 -m venv .venv
source .venv/bin/activate
```

### 4.2 Install Dependencies

```bash
pip install -r requirements.txt
```

### 4.3 Environment Variables

Create a .env file:

```env
DATABASE_URL=sqlite:///./ai_expense_tracker.db
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
RAG_ENABLED=true
```

### 4.4 Initialize Database

```bash
python db/init_db.py
```

### 4.5 Run Backend

```bash
uvicorn main:app --reload
```

## 5. Frontend Setup

```bash
cd Frontend
pnpm install
```

Create .env.local:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

Run frontend:

```bash
pnpm dev
```

## 6. Typical Workflow

```bash
ollama serve
cd Backend
uvicorn main:app --reload
cd Frontend
pnpm dev
```

Visit: http://localhost:3000

## 7. Submission Instructions

Zip folder:

```bash
cd ..
zip -r Ai-Expese-Tracker.zip Ai-Expese-Tracker
```

Or upload GitHub link.

