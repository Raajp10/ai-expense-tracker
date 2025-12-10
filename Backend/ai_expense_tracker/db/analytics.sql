-- ============================================
-- Analytics Queries for AI Expense Tracker
-- Step 4 – SQL + Relational Algebra targets
-- ============================================

PRAGMA foreign_keys = ON;

------------------------------------------------
-- Q1: Total monthly expense per user
-- (All users, all months)
------------------------------------------------
-- Relational Algebra version: RA1 (see notes)
SELECT
    t.user_id,
    SUBSTR(t.transaction_date, 1, 7) AS month,   -- 'YYYY-MM'
    SUM(t.amount) AS total_expense
FROM transactions t
JOIN categories c ON t.category_id = c.id
WHERE c.type = 'expense'
GROUP BY t.user_id, month
ORDER BY t.user_id, month;


------------------------------------------------
-- Q2: Total expense per category for a user in a month
-- Replace :user_id and :month with real values, e.g. 1, '2025-12'
------------------------------------------------
-- Relational Algebra version: RA2
SELECT
    c.name AS category,
    SUM(t.amount) AS total_expense
FROM transactions t
JOIN categories c ON t.category_id = c.id
WHERE t.user_id = :user_id
  AND c.type = 'expense'
  AND SUBSTR(t.transaction_date, 1, 7) = :month
GROUP BY c.id, c.name
ORDER BY total_expense DESC;


------------------------------------------------
-- Q3: Top 3 categories by spending for a user in a month
------------------------------------------------
SELECT
    c.name AS category,
    SUM(t.amount) AS total_expense
FROM transactions t
JOIN categories c ON t.category_id = c.id
WHERE t.user_id = :user_id
  AND c.type = 'expense'
  AND SUBSTR(t.transaction_date, 1, 7) = :month
GROUP BY c.id, c.name
ORDER BY total_expense DESC
LIMIT 3;


------------------------------------------------
-- Q4: Monthly total spending trend for one user
------------------------------------------------
-- Relational Algebra version: RA3
SELECT
    SUBSTR(t.transaction_date, 1, 7) AS month,
    SUM(t.amount) AS total_expense
FROM transactions t
JOIN categories c ON t.category_id = c.id
WHERE t.user_id = :user_id
  AND c.type = 'expense'
GROUP BY month
ORDER BY month;


------------------------------------------------
-- Q5: Categories where spending exceeded budget
-- For a given user (all months)
------------------------------------------------
-- Relational Algebra version: RA4
SELECT
    c.name AS category,
    b.month,
    b.amount AS budget_amount,
    IFNULL(SUM(t.amount), 0) AS actual_spent
FROM budgets b
JOIN categories c
  ON b.category_id = c.id
LEFT JOIN transactions t
  ON t.user_id = b.user_id
 AND t.category_id = b.category_id
 AND SUBSTR(t.transaction_date, 1, 7) = b.month
WHERE b.user_id = :user_id
GROUP BY c.name, b.month, b.amount
HAVING IFNULL(SUM(t.amount), 0) > b.amount
ORDER BY b.month, c.name;


------------------------------------------------
-- Q6: Category percentage share of total monthly expense
-- For one user + month
------------------------------------------------
SELECT
    c.name AS category,
    SUM(t.amount) AS total_spent,
    ROUND(
      SUM(t.amount) * 100.0 /
      (
        SELECT SUM(t2.amount)
        FROM transactions t2
        JOIN categories c2 ON t2.category_id = c2.id
        WHERE t2.user_id = :user_id
          AND c2.type = 'expense'
          AND SUBSTR(t2.transaction_date, 1, 7) = :month
      ),
      2
    ) AS percent_share
FROM transactions t
JOIN categories c ON t.category_id = c.id
WHERE t.user_id = :user_id
  AND c.type = 'expense'
  AND SUBSTR(t.transaction_date, 1, 7) = :month
GROUP BY c.id, c.name
ORDER BY percent_share DESC;


------------------------------------------------
-- Q7: Average daily expense in a month
-- For one user + month
------------------------------------------------
-- (You can also select the inner query alone to see per-day totals)
SELECT
    AVG(daily_total) AS avg_daily_expense
FROM (
    SELECT
        t.transaction_date,
        SUM(t.amount) AS daily_total
    FROM transactions t
    JOIN categories c ON t.category_id = c.id
    WHERE t.user_id = :user_id
      AND c.type = 'expense'
      AND SUBSTR(t.transaction_date, 1, 7) = :month
    GROUP BY t.transaction_date
) AS per_day;


------------------------------------------------
-- Q8: Highest single expense transaction in a period
------------------------------------------------
SELECT
    t.id,
    t.user_id,
    c.name AS category,
    t.amount,
    t.transaction_date,
    t.description
FROM transactions t
JOIN categories c ON t.category_id = c.id
WHERE t.user_id = :user_id
  AND c.type = 'expense'
  AND t.transaction_date BETWEEN :start_date AND :end_date
ORDER BY t.amount DESC
LIMIT 1;
