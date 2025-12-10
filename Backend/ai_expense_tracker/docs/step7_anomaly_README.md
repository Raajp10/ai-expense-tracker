# Step 7 – Anomaly Detection (Z-score)
**AI-Powered Expense Tracker – DBMS Final Project**  
Author: Raaj Patel  

---

## 1. Goal

This step adds **statistical anomaly detection** on top of the transaction data.

We detect **unusual daily spending patterns** for each user and month using the
**Z-score** method, which is a simple but effective way to identify outliers.

---

## 2. Method: Daily Z-score

For a given user `u` and month `m`:

1. Aggregate **total daily expense**:
   - Group all `transactions` of type `expense` by `transaction_date`.
2. Compute:
   - Mean daily spending:  
     \[
     \mu = \frac{1}{n} \sum_{i=1}^n x_i
     \]
   - Standard deviation (sample):  
     \[
     \sigma = \sqrt{\frac{1}{n-1} \sum_{i=1}^n (x_i - \mu)^2}
     \]
   where \(x_i\) is the total spent on day \(i\).
3. For each day, compute the Z-score:
   \[
   z_i = \frac{x_i - \mu}{\sigma}
   \]
4. A day is flagged as an **anomaly** if:
   \[
   |z_i| \ge \text{threshold}
   \]
   (In this project we typically use threshold = 2.0, but it is configurable.)

If there is only 1 day or all days have the same total, \(\sigma = 0\) and no anomalies are flagged.

---

## 3. Implementation Details

### Backend file: `backend/anomaly.py`

- Function `detect_daily_anomalies(db, user_id, month, z_threshold)`:

  - Queries `transactions` joined with `categories`.
  - Filters `categories.type = 'expense'`.
  - Filters by given `user_id` and `month` (`SUBSTR(date,1,7) = 'YYYY-MM'`).
  - Groups by `transaction_date` to compute daily totals.
  - Computes mean and standard deviation in Python.
  - Returns a list of points with:
    - `date`
    - `total_amount`
    - `z_score`
    - `is_anomaly` (true/false)

### Pydantic models (in `backend/schemas.py`)

- `DailyAnomalyPoint`
- `DetectDailyAnomaliesRequest`
- `DetectDailyAnomaliesResponse`

### API Endpoint (in `backend/main.py`)

```http
POST /anomalies/daily

✅ Step 7 – Additional Implemented Features
(Extended Anomaly Detection — Future Work Completed)

In addition to basic daily Z-score anomaly detection, the system has been extended with several advanced features that were originally listed under “Future Work.”

These enhancements make the analytics more realistic, powerful, and closer to real-world financial anomaly detection systems.

1. Per-Category Daily Anomaly Detection

Endpoint:

POST /anomalies/daily/by-category


This feature detects anomalies inside a single spending category, such as:

Food

Travel

Shopping

Entertainment

How it works

Only transactions matching category_name are grouped by day.

Z-score is computed using daily totals for that category.

Identifies days where spending on that one category is unusually high.

Example use

“Show anomalies only for ‘Food’ category in December.”

2. Transaction-Level Anomaly Detection

Endpoint:

POST /anomalies/transactions


This finds individual suspicious transactions rather than whole days.

Useful for detecting:

Accidental double purchases

Fraudulent charges

Very large single expenses

How it works

Computes Z-score on each transaction’s amount

Flags transactions far from the normal range

Returns:

amount

description

category

z-score

anomaly flag

3. Daily Plot Series (mean ± 2σ bands)

Endpoint:

POST /anomalies/daily/plot


This endpoint provides clean data for graphs:

mean

std

upper_band = mean + 2σ

lower_band = mean - 2σ

Daily totals

Use case

This is used to draw a chart like:

 ^ amount
 |
 |         ● (anomaly)
 |     ●
 |—————————————— upper band (mean + 2σ)
 |   ●
 |—————— mean
 |  ●
 |—————————————— lower band (mean - 2σ)
 | ●
 +---------------------------------> days


Great for:

Visualizing spikes

Presentation slides

Report graphs

4. RAG Integration — “Explain the anomaly”

The RAG system now supports questions like:

“Why is 2025-12-03 anomalous?”

This calls:

explain_anomalous_date()


and returns:

The total spent that day

The normal average

The z-score

The categories contributing most

The biggest individual transactions

Example response

“On 2025-12-03 you spent 81.00, which is much higher than your daily average of 18.25 (z=3.12).
Most spending came from Food: 54.00 and Transport: 22.00.
The largest transactions were Pizza (13.00) and Uber (11.00).”

✔ These extensions complete all the “Future Work” items for Step 7

You now have:

Daily anomalies

Per-category anomalies

Transaction-level anomalies

Plot-ready daily series for graphs

RAG explanations for anomalies

Everything is implemented, documented, and API-ready.