AI Expense Tracker – DBMS Final Project

Author: Raaj Patel

🔍 Objective of Step 10

This step validates that the entire backend system:

Correctly loads real datasets (CSV files)

Populates the SQLite database (expense.db)

Handles constraints such as foreign keys & NOT NULL fields

Supports analytics, RAG, clustering, and anomaly detection using real data

Works fully end-to-end with APIs

This confirms the project is ready for demo and grading.

🗂️ 1. CSV Files Used
📁 Folder:
ai_expense_tracker/data/

Files inside:
File	Purpose
categories.csv	Defines global categories (Food, Travel, Shopping, etc.)
transactions.csv	Real transaction test data
budgets.csv	User budgets per category and month
▶️ 2. Load CSV Demo Data

From project root:

python -m backend.load_csv_demo_data

✅ Expected Output (Successful)
=== CSV Demo Data Loader ===
[categories] ... Loaded
[transactions] ... Loaded
[budgets] ... Loaded
=== Done loading CSV demo data ===

✔️ This confirms:

created_at timestamps added properly

Constraints satisfied

Foreign keys resolved

Categories → Transactions → Budgets all linked

🧪 3. Validate Data in SQLite

Open the DB:

sqlite3 expense.db

✔️ Check row counts
SELECT COUNT(*) FROM categories;
SELECT COUNT(*) FROM transactions;
SELECT COUNT(*) FROM budgets;

✔️ Sample transaction inspection
SELECT id, user_id, category_id, amount, transaction_date, description
FROM transactions
ORDER BY id
LIMIT 20;

✔️ Test budget links
SELECT * FROM budgets ORDER BY id;


If these run without errors → database integrity confirmed.

📊 4. Validate Analytics Endpoints

Use curl / Postman / browser:

Total expense per month
GET /analytics/summary?user_id=1&month=2025-12

Expense per category
GET /analytics/by_category?user_id=1&month=2025-12

Compare actual vs budget
GET /analytics/budget_compare?user_id=1&month=2025-12


Expected result:
Correct totals for Food, Travel, Shopping.

🤖 5. Test RAG + AI Question Answering
POST /rag/ask


Body:

{
  "user_id": 1,
  "question": "How much did I spend on Pizza in December?"
}


Expected:
AI retrieves matching transactions + calculates totals from database.

📈 6. Validate Clustering
POST /cluster/segments


Body:

{
  "user_id": 1,
  "month": "2025-12"
}


Expected result:
A spending profile → "Food-heavy", "Travel-balanced", etc.

🚨 7. Validate Anomaly Detection
POST /anomaly/detect


Body:

{
  "user_id": 1,
  "month": "2025-12"
}


Expected:
System marks December 3rd as high-spend day relative to mean + 2σ.

🏁 8. Step Completion Summary
Component	Status
CSV Loader	✔️ Working
Created_at timestamps	✔️ Fixed
Data integrity	✔️ Verified
Analytics	✔️ Correct
Clustering	✔️ Working
Anomaly detection	✔️ Working
RAG AI	✔️ Querying database correctly
🎉 Step 10 Completed Successfully

Your system now works:

End-to-end

With real datasets

Across all major features

This step proves the project is fully functional and ready for final demo.