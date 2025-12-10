PRAGMA foreign_keys = ON;

-- Index to speed up filtering by user and date
CREATE INDEX IF NOT EXISTS idx_transactions_user_date
ON transactions(user_id, transaction_date);

-- Index to speed up category lookups for each user
CREATE INDEX IF NOT EXISTS idx_categories_user
ON categories(user_id);

-- Index for budgets lookups
CREATE INDEX IF NOT EXISTS idx_budgets_user_month
ON budgets(user_id, month);

-- Index for category_id filters (joins)
CREATE INDEX IF NOT EXISTS idx_transactions_category
ON transactions(category_id);

-- Index for categories.name (used in ORDER BY)
CREATE INDEX IF NOT EXISTS idx_categories_name
ON categories(name);
