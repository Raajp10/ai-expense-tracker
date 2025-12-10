-- Enable foreign key support in SQLite
PRAGMA foreign_keys = ON;

-- =========================
-- Table: users
-- =========================
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT        NOT NULL,
    email         TEXT        NOT NULL UNIQUE,
    password_hash TEXT        NOT NULL,
    created_at    TEXT        NOT NULL DEFAULT (datetime('now'))
);

-- =========================
-- Table: categories
-- Each category belongs to one user
-- =========================
CREATE TABLE IF NOT EXISTS categories (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER     NOT NULL,
    name       TEXT        NOT NULL,
    type       TEXT        NOT NULL CHECK (type IN ('expense','income')),
    created_at TEXT        NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =========================
-- Table: transactions
-- Every income/expense entry
-- =========================
CREATE TABLE IF NOT EXISTS transactions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER     NOT NULL,
    category_id      INTEGER     NOT NULL,
    amount           REAL        NOT NULL,      -- positive number
    transaction_date TEXT        NOT NULL,      -- ISO date string: YYYY-MM-DD
    description      TEXT,
    created_at       TEXT        NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id)     REFERENCES users(id)      ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- =========================
-- Table: budgets
-- Monthly budget per user/category
-- =========================
CREATE TABLE IF NOT EXISTS budgets (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER     NOT NULL,
    category_id INTEGER    NOT NULL,
    month      TEXT        NOT NULL,  -- e.g. '2025-12'
    amount     REAL        NOT NULL,
    created_at TEXT        NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id)     REFERENCES users(id)      ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- =========================
-- Table: monthly_summaries
-- For RAG-style Q&A and analytics
-- =========================
CREATE TABLE IF NOT EXISTS monthly_summaries (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER     NOT NULL,
    month         TEXT        NOT NULL,  -- 'YYYY-MM'
    total_spent   REAL        NOT NULL DEFAULT 0.0,
    total_income  REAL        NOT NULL DEFAULT 0.0,
    summary_text  TEXT,
    created_at    TEXT        NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
