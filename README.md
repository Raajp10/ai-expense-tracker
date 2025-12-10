# AI Expense Tracker with RAG-Enhanced Financial Reasoning

Course: Database Systems (Final Project)  
Student: Raaj Patel   
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
│   └── backend/
│       ├── __init__.py
│       ├── anomaly.py
│       ├── cluster.py
│       ├── db.py
│       ├── load_csv_demo_data.py
│       ├── main.py
│       ├── models.py
│       ├── rag.py
│       ├── rulebased_rag.py
│       ├── schemas.py
│       ├── requirements.txt
│       ├── .venv/                 # Python virtual environment
│       ├── __pycache__/           # Python cache
│       ├── data/
│       │   ├── budgets.csv
│       │   ├── categories.csv
│       │   └── transactions.csv
│       ├── db/
│       │   ├── analytics.sql
│       │   ├── indexes.sql
│       │   └── schema.sql
│       ├── docs/
│       │   ├── erd.md
│       │   └── requirements.md
│       ├── Image/
│       │   ├── ER_Diagram.png
│       │   ├── RDB_Text.png
│       │   └── RDB.png
│       └── expense.db             # SQLite database file
│
└── Frontend/
    ├── app/
    │   ├── anomalies/
    │   │   └── page.tsx
    │   ├── assistant/
    │   ├── budgets/
    │   ├── profile/
    │   ├── transactions/
    │   ├── globals.css
    │   ├── layout.tsx
    │   └── page.tsx
    │
    ├── components/
    │   └── ui/
    │       ├── app-provider.tsx
    │       ├── app-sidebar.tsx
    │       ├── client-layout.tsx
    │       ├── theme-provider.tsx
    │       └── top-bar.tsx
    │
    ├── hooks/
    │   ├── use-mobile.ts
    │   └── use-toast.ts
    │
    ├── lib/
    │   ├── api.ts
    │   └── utils.ts
    │
    ├── public/
    │
    ├── styles/
    │   └── globals.css
    │
    ├── components.json
    ├── next-env.d.ts
    ├── next.config.mjs
    ├── package.json
    ├── pnpm-lock.yaml
    ├── postcss.config.mjs
    ├── tailwind.config.ts   (if present)
    ├── tsconfig.json
    └── README.md   (optional frontend-only readme)

```

## 2. Key Features

- Natural-language queries over spending data
- RAG pipeline that converts questions → SQL → retrieved context → grounded answer
- Local-only processing (SQLite + FastAPI + Ollama on your machine)
- Budget vs Actual comparisons per category
- Simple anomaly detection (high-spend days and categories)
- Interactive dashboard built with Next.js (run using pnpm)

## 3. Prerequisites and Technologies Used

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

### Optional (for LLM / RAG Features)

To enable natural-language explanations using a local LLM, install **Ollama** on your system.

**Install Ollama (Official Download):**  
https://ollama.com/download

After installation, pull at least one model (recommended: Llama 3.2):

```bash
ollama pull llama3.2
```

## 4. Backend Setup

All backend commands are run from the Backend/ directory.

### 4.1 Virtual Environment

```bash
cd Backend/backend
python3.11 -m venv .venv
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

### 4.4 Run Backend

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
ollama pull llama3.2
cd Backend
uvicorn main:app --reload
cd Frontend
pnpm dev
```

Visit: http://localhost:3000


