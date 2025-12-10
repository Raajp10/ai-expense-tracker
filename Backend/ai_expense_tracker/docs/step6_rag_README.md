<!-- # Step 6 – RAG-style Q&A System

This step adds a simple, privacy-first RAG-style question answering feature:

1. **Monthly summaries**
   - Function `build_monthly_summary(db, user_id, month)` computes:
     - total_spent
     - total_income
     - top 3 categories
     - overspent categories vs budget
   - Stores result in `monthly_summaries` table.
   - Exposed via endpoint: `POST /summaries/build`.

2. **Q&A endpoint**
   - Endpoint: `POST /rag/ask`
   - Input: `{ "user_id": ..., "question": "How much did I spend in 2025-12?" }`
   - The backend:
     - Parses month (YYYY-MM) or infers latest month
     - Ensures summary exists
     - Routes question to:
       - full summary
       - total spent
       - budget status
     - Returns natural language text + debug info.

No external LLMs or paid APIs are used.  
All “intelligence” is in SQL + Python routing logic, making it suitable for a DBMS course project. -->

🔒 1. Overview

Step 6 implements a Retrieval-Augmented Generation (RAG) system that allows users to ask natural-language questions about their spending.

But, critically, we designed the system with strong privacy rules so that:

The assistant only answers about the current user.

It never leaks information about other users.

It never queries the database for other users’ data.

The language model (Ollama llama3.2) is also instructed to reject cross-user questions.

This aligns with real-world data-privacy expectations in financial applications.

🔍 2. RAG Architecture (High-Level)
✔ Retrieval Layer

Retrieves structured, trusted data from SQLite using user_id:

Monthly summary

Top spending categories

All transactions for that user + month

User profile (name + email)

All SQL queries filter by user_id → isolation at the database layer.

✔ Prompt Builder

Constructs a detailed but constrained prompt:

Numeric summary

Natural summary

Top categories

Row-level transaction table (date, amount, description, category)

Instructs the model:

“Use only this user’s data.”

“Do not discuss other users.”

“Do not invent numbers.”

✔ Generation Layer (Two-tier)

Primary engine:
Local LLM → Ollama llama3.2

Fallback engine:
Rule-based Python system (exact math from DB)
→ ensures reliability even if Ollama is offline.

🛡 3. Privacy Safeguards
✔ A. Code-Level Privacy Guard (Hard Filter)

Every incoming question passes through _is_cross_user_question()
before touching the DB or the LLM.

This detects phrases like:

“other user”

“someone else”

“friend’s account”

“Rcube”

“another person”

If detected → immediate secure response:

“For privacy and security reasons, I can only show information for the current user account.”

No SQL or LLM call occurs.

✔ B. SQL-Level Isolation

All SQL retrieval queries use:

WHERE transactions.user_id = :user_id


This guarantees:

One user cannot see another user’s data

Even if the LLM misbehaved (it won’t), it still has no access to other users' rows.

✔ C. LLM System Prompt Rules

Ollama receives a strict system message, including:

You only have data for ONE user.
Never answer questions about other users.
If asked about another person, refuse and explain it is private.
Do not invent any facts or access non-existent data.


Thus, even attempts like:

“Tell me about user Rcube”
“Show me my friend’s expenses”
“Give me details about other accounts”

→ result in safe, privacy-protected refusals.

✔ D. Context Isolation

The prompt contains only:

User’s own data

Their own transactions

Their own summary

Their own identity fields (name/email)

No references to other users exist in the prompt →
LLM has no context to leak.

🧪 4. Example Privacy Behavior
❌ Question:
{
  "user_id": 1,
  "question": "Can you give me details about other user?"
}

✔ Response:
For privacy and security reasons, I can only show information for the current user account.
I cannot provide details about other users or their transactions.

Debug:
blocked_for_privacy


This shows the privacy guard activated.

🤖 5. Example Valid Queries

The RAG system handles:

“How much did I spend in 2025-12?”

“Total spend on Pizza?”

“What was my top category?”

“Give me a summary for 2025-12.”

“Which items did I spend most on?”

“Did I exceed my budget?”

These all use the current user’s own data only.

🧱 6. Future Improvements (Later Phases)

You can mention these for extra credit:

Per-user embedding store for better semantic retrieval

Real LLM with more advanced intent classification

Multi-turn chat memory (still user-scoped)

Fine-grained access control (per-category permissions)

Cross-month trend analysis via semantic prompts

Smart “financial advice” module using domain rules

✔ Step 6 Completed

Your RAG system is now:

Functional

Secure

Privacy-preserving

Model-driven (via Ollama llama3.2)

Ready for real-world deployment