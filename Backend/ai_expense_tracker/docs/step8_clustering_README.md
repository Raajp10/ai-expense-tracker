
📘 Step 8 – Clustering & Segmentation (Advanced ML + Temporal Features)
AI-Powered Expense Tracker – DBMS Final Project
Author: Raaj Patel

🧩 1. Overview
Step 8 transforms raw transaction data into user spending profiles using:

✅ Extended feature engineering
✅ Temporal behavior signals
✅ True ML Clustering (K-Means & GMM)
✅ Rule-based segmentation fallback
✅ RAG Integration (“Food-heavy in Dec → Balanced in Jan”)
These provide intelligent, interpretable spending insights.

This layer turns your expense tracker into an AI financial assistant, not just a CRUD app.

🧠 2. Feature Engineering (Extended Vector)
Each user’s monthly vector includes:

2.1 Category Features
For every category:

Total spent

Ratio of category spend to monthly total

Example:

Category	Total	Ratio
Food	81	1.00
Travel	0	0

2.2 Temporal Features
These describe behavior, not just amounts:

✔ Number of transactions (tx_count)
Indicates activity level.

✔ Standard deviation of daily spending (daily_std)
Measures consistency vs spikes.

✔ Weekend spending ratio (weekend_ratio)
If > 0.5 → weekends dominate spending.

2.3 Final Feature Vector
Final vector structure:

css
Copy code
[ totals..., ratios..., tx_count, daily_std, weekend_ratio ]
This vector works for:

Rule-based segmentation

KMeans clustering

GMM clustering

RAG insights

🔍 3. Rule-Based Segmentation (Always Available)
This is the fallback segmentation:

Labels:
Inactive

Light Spender

Big Spender

Balanced Spender

Food-heavy, Travel-heavy, etc. (if category ratio ≥ 70%)

Why rule-based?
Works even with 1 user

Easy to explain to professors

No ML dependency errors

🤖 4. True ML Clustering (KMeans & GMM)
When the dataset has multiple users, we run real clustering:

4.1 K-Means
Groups users into k clusters using Euclidean distance

Good for simple segmentation

4.2 GMM (Gaussian Mixture Model)
Creates soft clusters

Captures overlapping spending behaviors

More realistic for real-world finance data

✔ Function: global_kmeans_clusters(...)
Outputs:

json
Copy code
{
  "user_id": 5,
  "cluster_id": 2,
  "label": "KMeans-Cluster-2"
}
✔ Function: global_gmm_clusters(...)
Outputs:

json
Copy code
{
  "user_id": 3,
  "cluster_id": 1,
  "label": "GMM-Cluster-1"
}
📅 5. Monthly Trend Comparison (RAG Integration)
Users can ask:

“Compare my spending between 2025-12 and 2026-01.”

The system extracts months using regex and generates a full explanation:

Example Output
In 2025-12, your segment was Food-heavy with 81.00.
In 2026-01, you are Balanced Spender, dominant in Shopping.
Your spending pattern changed significantly between the two months.

This integrates:

Category ratios

Totals per month

Segmentation labels

Temporal variance

🏷 6. API Endpoints Summary
6.1 Personal Monthly Segmentation
bash
Copy code
POST /cluster/segments
Result contains:

totals

ratios

tx_count

daily_std

weekend_ratio

rule-based label

6.2 Global ML Clustering Across All Users
pgsql
Copy code
POST /cluster/global
Body:

json
Copy code
{
  "month": "2025-12",
  "algo": "kmeans",
  "n_clusters": 4
}
Returns cluster ID for each user.

6.3 RAG-driven Trend Comparison
bash
Copy code
POST /rag/ask
Example:

json
Copy code
{
  "user_id": 1,
  "question": "How did my spending change between 2025-12 and 2026-01?"
}
Produces a natural-language explanation.

🧪 7. Implementation Summary
Implemented in backend/cluster.py:
Extended feature vector

Rule-based segmentation

KMeans clustering

GMM clustering

User feature extraction for all users

Temporal analysis utilities

Implemented in backend/rag.py:
Month comparison extraction

Trend reasoning using segments

Safety: no cross-user data access

🚀 8. Why This Matters (Professor-Friendly Explanation)
This step transforms your expense tracker into an intelligent system:

✔ Learns patterns
✔ Detects behavior changes
✔ Clusters users realistically
✔ Computes advanced features
✔ Generates explanations via LLM
✔ Follows privacy rules
Essentially, you’ve implemented:

“AI-powered Personal Finance Pattern Mining.”

Which is graduate-level work, beyond a normal DBMS final project.

📌 9. Future Extensions (Optional)
Seasonal clustering (Year-over-Year)

Embedding-based segment prediction (Neural Networks)

Auto-ML for cluster selection

Real-time drift detection

✅ Step 8 Completed
You now have:

✔ Advanced ML segmentation
✔ Temporal-aware feature engineering
✔ Real KMeans & GMM clustering
✔ Monthly behavior trend explanation
✔ Fully integrated RAG reasoning

