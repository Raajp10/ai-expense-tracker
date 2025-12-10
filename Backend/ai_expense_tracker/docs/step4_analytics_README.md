# Step 4 – Analytics Queries + Relational Algebra  
**AI-Powered Expense Tracker – DBMS Final Project**  
Author: *Raaj Patel*  

---

## 📌 Overview
This step adds **analytical queries** and **relational algebra expressions** to support insights such as monthly spending, category trends, budget comparisons, and top categories.  
These analytics also support later AI modules (RAG, anomaly detection, clustering).

---

# 1. SQL ANALYTICS QUERIES

Below are the 8 analytics queries implemented in `analytics.sql`.

---

## **Q1 – Total Monthly Expense per User**

### **SQL**
```sql
SELECT
    t.user_id,
    SUBSTR(t.transaction_date, 1, 7) AS month,
    SUM(t.amount) AS total_expense
FROM transactions t
JOIN categories c ON t.category_id = c.id
WHERE c.type = 'expense'
GROUP BY t.user_id, month
ORDER BY t.user_id, month;

# Step 4 – Analytics Queries + Relational Algebra  
**AI-Powered Expense Tracker – DBMS Final Project**  
Author: *Raaj Patel*  

---

## 📌 Overview
This step adds **analytical queries** and **relational algebra expressions** to support insights such as monthly spending, category trends, budget comparisons, and top categories.  
These analytics also support later AI modules (RAG, anomaly detection, clustering).

---

# 1. SQL ANALYTICS QUERIES

Below are the 8 analytics queries implemented in `analytics.sql`.

---

## **Q1 – Total Monthly Expense per User**

### **SQL**
```sql
SELECT
    t.user_id,
    SUBSTR(t.transaction_date, 1, 7) AS month,
    SUM(t.amount) AS total_expense
FROM transactions t
JOIN categories c ON t.category_id = c.id
WHERE c.type = 'expense'
GROUP BY t.user_id, month
ORDER BY t.user_id, month;
Relational Algebra (RA1)
mathematica
Copy code
E = σ(C.type='expense') (T ⋈_{T.category_id=C.id} C)
γ user_id, month ; SUM(amount)→total_expense (E)
Q2 – Total Expense per Category for a User in a Month
SQL
sql
Copy code
SELECT
    c.name AS category,
    SUM(t.amount) AS total_expense
FROM transactions t
JOIN categories c ON t.category_id = c.id
WHERE t.user_id = 1
  AND c.type = 'expense'
  AND SUBSTR(t.transaction_date, 1, 7) = '2025-12'
GROUP BY c.id, c.name
ORDER BY total_expense DESC;
Relational Algebra (RA2)
mathematica
Copy code
E = σ(C.type='expense') (T ⋈ C)
F = σ(T.user_id=u ∧ prefix_7(T.date)=m) (E)
γ C.id, C.name ; SUM(amount)→total_expense (F)
Q3 – Top 3 Categories by Spending (User + Month)
SQL
sql
Copy code
SELECT
    c.name,
    SUM(t.amount) AS total_expense
FROM transactions t
JOIN categories c ON t.category_id=c.id
WHERE t.user_id=1
  AND c.type='expense'
  AND SUBSTR(t.transaction_date,1,7)='2025-12'
GROUP BY c.id, c.name
ORDER BY total_expense DESC
LIMIT 3;
Q4 – Monthly Spending Trend for a User
SQL
sql
Copy code
SELECT
    SUBSTR(t.transaction_date,1,7) AS month,
    SUM(t.amount) AS total_expense
FROM transactions t
JOIN categories c ON t.category_id=c.id
WHERE t.user_id=1
  AND c.type='expense'
GROUP BY month
ORDER BY month;
Relational Algebra (RA3)
mathematica
Copy code
E = σ(C.type='expense') (T ⋈ C)
F = σ(T.user_id=u) (E)
γ month ; SUM(amount)→total_expense (F)
Q5 – Categories Where Spending Exceeded Budget
SQL
sql
Copy code
SELECT
    c.name AS category,
    b.month,
    b.amount AS budget_amount,
    IFNULL(SUM(t.amount),0) AS actual_spent
FROM budgets b
JOIN categories c ON b.category_id=c.id
LEFT JOIN transactions t
  ON t.user_id=b.user_id
 AND t.category_id=b.category_id
 AND SUBSTR(t.transaction_date,1,7)=b.month
WHERE b.user_id=1
GROUP BY c.name, b.month, b.amount
HAVING actual_spent > b.amount
ORDER BY b.month, c.name;
Relational Algebra (RA4)
makefile
Copy code
BC  = B ⋈_{B.category_id=C.id} C
BCT = BC ⟕_{matching month/category/user} T
F   = σ(B.user_id=u) (BCT)
G   = γ C.name, B.month, B.amount ; SUM(T.amount)→actual_spent (F)
σ(actual_spent > amount)(G)
2. HOW TO RUN QUERIES IN SQLITE
bash
Copy code
sqlite3 expense.db
.headers on
.mode column

-- Example:
SELECT * FROM transactions;
Or load all analytics queries:

bash
Copy code
.read db/analytics.sql
3. OUTPUT SCREENSHOTS
Screenshots of each query will be included in the final report 