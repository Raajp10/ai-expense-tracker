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

### ⚠️ Important: LLM / RAG Requirements

This project supports two modes of operation:

1. **LLM-powered RAG mode** (recommended)
2. **Rule-based fallback mode** (automatic backup)

To use the full RAG pipeline with natural-language explanations, you must install
and run **Ollama** locally:

- Download Ollama: https://ollama.com/download
- Pull at least one model: Example in these project test with ollama pull llama3.2

## 🔄 Using a Different AI Model (Replacing Ollama)

The backend is designed so you can easily switch from **Ollama** to **any other LLM provider**, such as:

- OpenAI (GPT-4, GPT-4o, GPT-3.5)
- Groq (Llama-3, Mixtral Ultra-Fast)
- DeepSeek-R1 / DeepSeek-Chat
- HuggingFace Inference API
- Local models via LM Studio
- Custom inference servers (vLLM, TGI, llama.cpp, etc.)

Only **one file** must be modified:

### 🔧 Modify This Function to Use Any AI Provider

The function responsible for LLM communication is:

```python
def call_ollama_chat(prompt: str, model: str = "llama3.2") -> str:
```

### Replace Ollama with OpenAI
```python
def call_ollama_chat(prompt: str, model: str = "gpt-4o"):
    from openai import OpenAI
    client = OpenAI(api_key="YOUR_API_KEY")

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()
```
### Replace with Groq (Llama-3 Turbo / Mixtral)
```python
def call_ollama_chat(prompt: str, model: str = "llama3-70b-8192"):
    import requests, os
    headers = {"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"}

    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()
```

### Replace with HuggingFace Inference API
```python
def call_ollama_chat(prompt: str, model: str = "meta-llama/Meta-Llama-3-8B"):
    import requests, os
    HF_KEY = os.getenv("HF_TOKEN")

    response = requests.post(
        f"https://api-inference.huggingface.co/models/{model}",
        headers={"Authorization": f"Bearer {HF_KEY}"},
        json={"inputs": prompt},
    )
    text = response.json()[0]["generated_text"]
    return text.strip()
```
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

### for LLM / RAG Features

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
cd ai-expense-tracker/Backend/backend
python3.11 -m venv .venv
source .venv/bin/activate
```

### 4.2 Install Dependencies

```bash
pip install -r requirements.txt
```

### 4.3 Run Backend

```bash
uvicorn main:app --reload
```

## 5. Frontend Setup

```bash
cd Frontend
pnpm install
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


