# AI-Powered Personal Expense Tracker – Requirements

## 1. Problem Statement

Managing daily expenses is hard for students and working professionals.
People often:
- Forget where their money is going,
- Don’t track by category (Food, Rent, Travel, etc.),
- Don’t notice overspending until it’s too late.

This project builds a **personal expense tracking system** with:
1. A **database-backed app** to store users, categories, transactions, and budgets.
2. **Analytics queries** (SQL) to summarize and analyze spending.
3. **AI-inspired components** like:
   - Natural language Q&A (RAG-style) over monthly summaries,
   - Anomaly detection (unusual expenses),
   - Clustering of spending patterns.

The focus is on **database design, queries, and optimization**, plus a light layer of AI-style analytics.

---

## 2. Core Entities (Tables)

We design four main tables:

1. **users**
   - Stores basic information about each user of the system.

2. **categories**
   - Each user can define their own categories (Food, Rent, Travel, etc.).
   - Categories have a type: `expense` or `income`.

3. **transactions**
   - Every income or expense is stored as a transaction.
   - Linked to a user and a category.

4. **budgets**
   - Users can set a monthly budget per category (e.g., Food: $200 in Dec 2025).

Optionally (for RAG and analytics):

5. **monthly_summaries**
   - Precomputed text + numeric summaries per user per month.

---

## 3. Functional Requirements

### 3.1 Basic Operations (CRUD)

The system should support:

- **Users**
  - Create a new user.
  - View user details.
  - (Optionally) update or delete user.

- **Categories**
  - Add / edit / delete categories per user.
  - Each category has: name and type (`expense` or `income`).

- **Transactions**
  - Add a new transaction with:
    - user, category, amount, date, description
  - Edit / delete a transaction.
  - List transactions for a user (filter by date range and/or category).

- **Budgets**
  - Set a monthly budget per (user, category, month).
  - View budgets and compare actual spending vs budget.

---

## 4. Analytics & Queries (SQL Focus)

We will implement at least **8 SQL queries**, including for example:

1. Total expense per user per month.
2. Total expense per category in a given month.
3. Top 3 categories by spending for a user in a given month.
4. Monthly trend of total spending over time.
5. Categories where spending exceeded budget.
6. Percentage of each category in total monthly spend (category share).
7. Average daily spending in a month.
8. Highest single transaction in a period.

At least **2–3 queries** will also be expressed in **relational algebra** in the report/presentation.

We will also use `EXPLAIN` / `EXPLAIN ANALYZE` to compare query performance **before and after** adding indexes.

---

## 5. Database Internals

- Use **transactions** to ensure:
  - When inserting or updating a transaction, the changes are atomic.
- Use **indexes**, e.g.:
  - Index on `(user_id, transaction_date)` in `transactions`.
  - Index on `(user_id, category_id, month)` in `budgets`.
- Measure query performance using:
  - `EXPLAIN` or `EXPLAIN ANALYZE` (depending on DB engine).

---

## 6. AI / Data Components

### 6.1 RAG-Style Question Answering

- Generate a **monthly summary text** per user (e.g., “In Dec 2025 you spent $500… top category was Food…”).
- Store summaries in `monthly_summaries` table.
- Allow user to ask questions in natural language, such as:
  - “How much did I spend on food last month?”
  - “Which category was the highest in October?”
- Our system will:
  - Parse/route the question to the right SQL query or to the stored summary text.
  - Return a human-readable answer.

*(For this project, we can simulate this logic without paid LLM APIs.)*

### 6.2 Anomaly Detection (Z-score)

- Detect unusual transactions (e.g., much larger than normal).
- For each user:
  - Compute mean and standard deviation of their transaction amounts.
  - Mark transactions with high z-score (e.g., |z| > 2) as anomalies.
- Store or highlight these anomalies in reports.

### 6.3 Clustering (K-Means)

- Use k-means clustering on spending patterns, such as:
  - Total spending per category,
  - Or feature vectors like [Food, Rent, Travel, Shopping, …].
- Group months or users into clusters:
  - “Low spender”, “Balanced”, “High Food spending”, etc.

We will use **Python (pandas, numpy, scikit-learn)** for anomaly detection and clustering on top of the database data.

---

## 7. Non-Functional Requirements

- **Database**: SQLite (for development; design is portable to PostgreSQL).
- **Backend**: Python + FastAPI.
- **Privacy-first**: All processing is local, no paid external APIs.
- **Reproducibility**:
  - Include a SQL script to create tables and insert sample data.
  - Provide instructions to run the backend and analytics scripts.

---

## 8. Deliverables

1. **ERD diagram** (tables + relationships).
2. **Relational schema** and **SQL DDL** (`CREATE TABLE` statements).
3. **Sample data** (`INSERT` statements).
4. **SQL queries** (8+ analytics queries) + relational algebra for 2–3 of them.
5. **Indexing & transactions** demonstration with `EXPLAIN`/`ANALYZE`.
6. **RAG-style Q&A** demo script or API.
7. **Anomaly detection & clustering** scripts and results.
8. **Final report / presentation** summarizing design, experiments, and findings.
