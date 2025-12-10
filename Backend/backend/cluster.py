# from __future__ import annotations

# from typing import Dict, List
# from sqlalchemy import func
# from sqlalchemy.orm import Session
# import numpy as np
# from sklearn.cluster import KMeans

# from . import models


# def build_spending_feature_vector(db: Session, user_id: int, month: str) -> Dict:
#     """
#     Build a numeric feature vector based on category-wise spending distribution.
#     Includes:
#         - category totals
#         - ratio of each category to total expense
#     """
#     # 1) Get all categories
#     categories = db.query(models.Category).all()
#     category_names = [c.name for c in categories]

#     # 2) Compute totals for each category for this user/month
#     totals = {}
#     grand_total = 0.0

#     for name in category_names:
#         amount = (
#             db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0))
#             .join(models.Category, models.Transaction.category_id == models.Category.id)
#             .filter(models.Transaction.user_id == user_id)
#             .filter(models.Category.name == name)
#             .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
#             .scalar()
#         )
#         totals[name] = float(amount)
#         grand_total += float(amount)

#     # 3) Ratios
#     ratios = {}
#     for name in category_names:
#         if grand_total > 0:
#             ratios[name] = totals[name] / grand_total
#         else:
#             ratios[name] = 0.0

#     # Final embedding vector
#     vector = []
#     for name in category_names:
#         vector.append(totals[name])
#     for name in category_names:
#         vector.append(ratios[name])

#     return {
#         "categories": category_names,
#         "totals": totals,
#         "ratios": ratios,
#         "grand_total": grand_total,
#         "vector": vector,
#     }


# def cluster_user_profile(vector: List[float], n_clusters: int = 4) -> Dict:
#     """
#     Fit KMeans clustering on this single user's vector + synthetic anchors
#     to generate a stable cluster.
#     """
#     v = np.array(vector)

#     # Synthetic anchors for stable clustering
#     anchors = np.array([
#         np.zeros_like(v),         # Saver
#         np.ones_like(v) * 50,     # Big Spender
#         np.array([100, 0, 0, 0, 0] + [1, 0, 0, 0, 0]),  # Food-heavy
#         np.array([0, 100, 0, 0, 0] + [0, 1, 0, 0, 0]),  # Travel-heavy
#     ])

#     X = np.vstack([v, anchors])
#     kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
#     labels = kmeans.fit_predict(X)

#     # User is first element
#     user_label = int(labels[0])

#     # Label meaning
#     meaning = {
#         0: "Balanced Spender",
#         1: "Saver",
#         2: "Big Spender",
#         3: "Food-heavy",
#         # If >3 clusters, fallback
#     }

#     label_name = meaning.get(user_label, f"Cluster-{user_label}")

#     return {
#         "cluster_id": user_label,
#         "label": label_name,
#         "centroid": kmeans.cluster_centers_[user_label].tolist(),
#     }

from __future__ import annotations

from typing import Dict, List, Tuple
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

import models

# Optional ML dependencies
try:
    import numpy as np
    from sklearn.cluster import KMeans
    from sklearn.mixture import GaussianMixture

    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

def _is_weekend(date_str: str) -> bool:
    """
    date_str: 'YYYY-MM-DD' or 'YYYY-M-D'
    Returns True if Saturday or Sunday.
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        # try a more forgiving format
        dt = datetime.fromisoformat(date_str)
    return dt.weekday() >= 5  # 5 = Saturday, 6 = Sunday


def build_spending_feature_vector(db: Session, user_id: int, month: str) -> Dict:
    """
    Build a numeric feature vector based on:
      - category totals
      - category ratios
      - temporal features:
          * number of transactions in the month
          * std of daily spending
          * weekend vs weekday spending ratio (by amount)
    """

    # 1) All categories in DB
    categories = db.query(models.Category).all()
    category_names = [c.name for c in categories]

    # 2) Category totals & grand total (expense only)
    totals: Dict[str, float] = {}
    grand_total = 0.0

    for name in category_names:
        amount = (
            db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0))
            .join(models.Category, models.Transaction.category_id == models.Category.id)
            .filter(models.Transaction.user_id == user_id)
            .filter(models.Category.name == name)
            .filter(models.Category.type == "expense")
            .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
            .scalar()
        )
        totals[name] = float(amount)
        grand_total += float(amount)

    # 3) Ratios
    ratios: Dict[str, float] = {}
    for name in category_names:
        if grand_total > 0:
            ratios[name] = totals[name] / grand_total
        else:
            ratios[name] = 0.0

    # 4) Temporal features

    # 4a) number of expense transactions in the month
    tx_count = (
        db.query(models.Transaction)
        .join(models.Category, models.Transaction.category_id == models.Category.id)
        .filter(models.Transaction.user_id == user_id)
        .filter(models.Category.type == "expense")
        .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
        .count()
    )

    # 4b) std of daily spending
    daily_rows = (
        db.query(
            models.Transaction.transaction_date.label("date"),
            func.sum(models.Transaction.amount).label("total_amount"),
        )
        .join(models.Category, models.Transaction.category_id == models.Category.id)
        .filter(models.Transaction.user_id == user_id)
        .filter(models.Category.type == "expense")
        .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
        .group_by(models.Transaction.transaction_date)
        .all()
    )

    if daily_rows:
        daily_totals = [float(r.total_amount) for r in daily_rows]
        n = len(daily_totals)
        if n > 1:
            mean = sum(daily_totals) / n
            var = sum((x - mean) ** 2 for x in daily_totals) / (n - 1)
            daily_std = var ** 0.5
        else:
            daily_std = 0.0
    else:
        daily_std = 0.0

    # 4c) weekend vs weekday spending ratio
    weekend_total = 0.0
    weekday_total = 0.0

    tx_rows = (
        db.query(
            models.Transaction.transaction_date,
            models.Transaction.amount,
        )
        .join(models.Category, models.Transaction.category_id == models.Category.id)
        .filter(models.Transaction.user_id == user_id)
        .filter(models.Category.type == "expense")
        .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
        .all()
    )

    for date_str, amount in tx_rows:
        amount_f = float(amount)
        if _is_weekend(date_str):
            weekend_total += amount_f
        else:
            weekday_total += amount_f

    total_for_ratio = weekend_total + weekday_total
    if total_for_ratio > 0:
        weekend_ratio = weekend_total / total_for_ratio
    else:
        weekend_ratio = 0.0

    # 5) Final vector
    vector: List[float] = []

    # category totals
    for name in category_names:
        vector.append(totals[name])
    # category ratios
    for name in category_names:
        vector.append(ratios[name])
    # temporal features
    vector.append(float(tx_count))
    vector.append(float(daily_std))
    vector.append(float(weekend_ratio))

    return {
        "categories": category_names,
        "totals": totals,
        "ratios": ratios,
        "grand_total": grand_total,
        "tx_count": tx_count,
        "daily_std": daily_std,
        "weekend_ratio": weekend_ratio,
        "vector": vector,
    }

def cluster_user_profile(features: Dict) -> Dict:
    """
    Rule-based segmentation instead of KMeans.

    Uses:
      - grand_total
      - dominant category ratio
      - category name

    Returns a 'cluster_id' and human-readable 'label'.
    """
    categories: List[str] = features["categories"]
    totals: Dict[str, float] = features["totals"]
    ratios: Dict[str, float] = features["ratios"]
    grand_total: float = float(features["grand_total"])
    vector: List[float] = features["vector"]

    if grand_total == 0:
        return {
            "cluster_id": 0,
            "label": "Inactive",
            "centroid": vector,
        }

    # find dominant category
    max_cat = None
    max_ratio = -1.0
    for name in categories:
        r = ratios.get(name, 0.0)
        if r > max_ratio:
            max_ratio = r
            max_cat = name

    # simple thresholds (you can tune these)
    # assume amounts roughly in some realistic currency range
    if grand_total < 50:
        cluster_id = 1
        label = "Light Spender"
    elif grand_total > 500:
        cluster_id = 2
        label = "Big Spender"
    else:
        cluster_id = 3
        label = "Balanced Spender"

    # Override if one category dominates heavily
    if max_cat is not None and max_ratio >= 0.7:
        cluster_id = 4
        label = f"{max_cat}-heavy"

    return {
        "cluster_id": cluster_id,
        "label": label,
        "centroid": vector,  # for completeness, we just return the feature vector as 'centroid'
    }

def cluster_user_profile_rule_based(features: Dict) -> Dict:
    """
    Rule-based segmentation using grand_total + dominant category.
    """
    categories: List[str] = features["categories"]
    totals: Dict[str, float] = features["totals"]
    ratios: Dict[str, float] = features["ratios"]
    grand_total: float = float(features["grand_total"])
    vector: List[float] = features["vector"]

    if grand_total == 0:
        return {
            "cluster_id": 0,
            "label": "Inactive",
            "centroid": vector,
        }

    # dominant category
    max_cat = None
    max_ratio = -1.0
    for name in categories:
        r = ratios.get(name, 0.0)
        if r > max_ratio:
            max_ratio = r
            max_cat = name

    if grand_total < 50:
        cluster_id = 1
        label = "Light Spender"
    elif grand_total > 500:
        cluster_id = 2
        label = "Big Spender"
    else:
        cluster_id = 3
        label = "Balanced Spender"

    if max_cat is not None and max_ratio >= 0.7:
        cluster_id = 4
        label = f"{max_cat}-heavy"

    return {
        "cluster_id": cluster_id,
        "label": label,
        "centroid": vector,
    }

def collect_all_user_features_for_month(
    db: Session, month: str
) -> List[Tuple[int, Dict]]:
    """
    Collect features for all users who have any expense transactions in this month.
    Returns list of (user_id, features_dict).
    """
    user_ids = (
        db.query(models.Transaction.user_id)
        .join(models.Category, models.Transaction.category_id == models.Category.id)
        .filter(models.Category.type == "expense")
        .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
        .distinct()
        .all()
    )

    user_ids = [u[0] for u in user_ids]

    results: List[Tuple[int, Dict]] = []
    for uid in user_ids:
        feats = build_spending_feature_vector(db, uid, month)
        results.append((uid, feats))
    return results


def global_kmeans_clusters(
    db: Session, month: str, n_clusters: int = 4
) -> Dict[int, Dict]:
    """
    Run true K-Means across ALL users for a given month.
    Returns { user_id: {cluster_id, label} }
    """
    if not HAS_SKLEARN:
        raise RuntimeError("scikit-learn is not installed; cannot run KMeans clustering.")

    user_feats = collect_all_user_features_for_month(db, month)
    if len(user_feats) < 2:
        # not enough users to cluster meaningfully
        mapping = {}
        for uid, feats in user_feats:
            mapping[uid] = cluster_user_profile_rule_based(feats)
        return mapping

    X = np.array([feats["vector"] for _, feats in user_feats])

    kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    labels = kmeans.fit_predict(X)

    # simple label names based on cluster centers norm
    # (you can design smarter rules if you want)
    mapping: Dict[int, Dict] = {}
    for (uid, feats), lbl in zip(user_feats, labels):
        mapping[uid] = {
            "cluster_id": int(lbl),
            "label": f"KMeans-Cluster-{lbl}",
            "centroid": kmeans.cluster_centers_[lbl].tolist(),
        }

    return mapping


def global_gmm_clusters(
    db: Session, month: str, n_components: int = 4
) -> Dict[int, Dict]:
    """
    Run true GMM clustering across ALL users for a given month.
    Returns { user_id: {cluster_id, label} }
    """
    if not HAS_SKLEARN:
        raise RuntimeError("scikit-learn is not installed; cannot run GMM clustering.")

    user_feats = collect_all_user_features_for_month(db, month)
    if len(user_feats) < 2:
        mapping = {}
        for uid, feats in user_feats:
            mapping[uid] = cluster_user_profile_rule_based(feats)
        return mapping

    X = np.array([feats["vector"] for _, feats in user_feats])

    gmm = GaussianMixture(n_components=n_components, random_state=42)
    labels = gmm.fit_predict(X)

    mapping: Dict[int, Dict] = {}
    for (uid, feats), lbl in zip(user_feats, labels):
        mapping[uid] = {
            "cluster_id": int(lbl),
            "label": f"GMM-Cluster-{lbl}",
            "centroid": gmm.means_[lbl].tolist(),
        }

    return mapping
