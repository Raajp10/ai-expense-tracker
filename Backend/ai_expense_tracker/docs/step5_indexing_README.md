Why Indexing?

Indexes significantly improve read/query performance for analytical queries.
Without indexes, SQLite performs full table scans.
With indexes, queries become O(log n), enabling fast lookups.

Indexes Used
Table	Columns Indexed	Purpose
transactions	(user_id, transaction_date)	Fast monthly filtering
transactions	(category_id)	Faster join with categories
categories	(user_id)	Category lookup per user
categories	(name)	ORDER BY speed
budgets	(user_id, month)	Fast budget comparisons
EXPLAIN ANALYZE Examples
Before Indexing
EXPLAIN QUERY PLAN SELECT ...
SCAN TABLE transactions
SCAN TABLE categories

After Indexing
SEARCH TABLE transactions USING INDEX idx_transactions_user_date
SEARCH TABLE categories USING INDEX idx_categories_user


This shows index usage and validates optimization.

How to Run
sqlite3 expense.db < db/indexes.sql


Then:

EXPLAIN QUERY PLAN SELECT ...;
EXPLAIN ANALYZE SELECT ...;
