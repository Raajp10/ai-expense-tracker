from __future__ import annotations

from math import sqrt
from typing import Dict, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from . import models


def detect_daily_anomalies(
    db: Session,
    user_id: int,
    month: str,
    z_threshold: float = 2.0,
) -> Dict:
    """
    Detect anomalous daily spending for a given user and month using Z-score.

    Steps:
      1. Aggregate total expense per day.
      2. Compute mean and standard deviation of daily totals.
      3. Mark a day as anomaly if |z_score| >= z_threshold.
    """

    # 1) Aggregate daily totals (expense only)
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
        .order_by(models.Transaction.transaction_date.asc())
        .all()
    )

    if not daily_rows:
        # no data for that user/month
        return {
            "user_id": user_id,
            "month": month,
            "mean": 0.0,
            "std": 0.0,
            "z_threshold": z_threshold,
            "points": [],
        }

    totals = [float(row.total_amount) for row in daily_rows]
    n = len(totals)

    # 2) Compute mean
    mean = sum(totals) / n

    # 3) Compute standard deviation (sample std if n > 1)
    if n > 1:
        var = sum((x - mean) ** 2 for x in totals) / (n - 1)
        std = sqrt(var)
    else:
        std = 0.0

    points: List[Dict] = []
    for row in daily_rows:
        total = float(row.total_amount)
        if std > 0:
            z = (total - mean) / std
        else:
            z = 0.0  # if all days same, no anomalies

        is_anomaly = abs(z) >= z_threshold
        points.append(
            {
                "date": row.date,
                "total_amount": total,
                "z_score": z,
                "is_anomaly": is_anomaly,
            }
        )

    return {
        "user_id": user_id,
        "month": month,
        "mean": mean,
        "std": std,
        "z_threshold": z_threshold,
        "points": points,
    }

def detect_daily_anomalies_by_category(
    db: Session,
    user_id: int,
    month: str,
    category_name: str,
    z_threshold: float = 2.0,
) -> Dict:
    """
    Same as detect_daily_anomalies, but restricted to a single category (e.g. 'Food').
    Uses exact match on Category.name (you can change to ilike for fuzzy).
    """
    daily_rows = (
        db.query(
            models.Transaction.transaction_date.label("date"),
            func.sum(models.Transaction.amount).label("total_amount"),
        )
        .join(models.Category, models.Transaction.category_id == models.Category.id)
        .filter(models.Transaction.user_id == user_id)
        .filter(models.Category.type == "expense")
        .filter(models.Category.name == category_name)
        .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
        .group_by(models.Transaction.transaction_date)
        .order_by(models.Transaction.transaction_date.asc())
        .all()
    )

    if not daily_rows:
        return {
            "user_id": user_id,
            "month": month,
            "mean": 0.0,
            "std": 0.0,
            "z_threshold": z_threshold,
            "points": [],
            "scope": f"category={category_name}",
        }

    totals = [float(row.total_amount) for row in daily_rows]
    n = len(totals)
    mean = sum(totals) / n
    if n > 1:
        var = sum((x - mean) ** 2 for x in totals) / (n - 1)
        std = sqrt(var)
    else:
        std = 0.0

    points: List[Dict] = []
    for row in daily_rows:
        total = float(row.total_amount)
        if std > 0:
            z = (total - mean) / std
        else:
            z = 0.0
        is_anomaly = abs(z) >= z_threshold
        points.append(
            {
                "date": row.date,
                "total_amount": total,
                "z_score": z,
                "is_anomaly": is_anomaly,
            }
        )

    return {
        "user_id": user_id,
        "month": month,
        "mean": mean,
        "std": std,
        "z_threshold": z_threshold,
        "points": points,
        "scope": f"category={category_name}",
    }

def detect_transaction_anomalies(
    db: Session,
    user_id: int,
    month: str,
    z_threshold: float = 2.0,
) -> Dict:
    """
    Detect anomalous individual transactions using Z-score on transaction amounts.
    """
    tx_rows = (
        db.query(
            models.Transaction.id,
            models.Transaction.transaction_date,
            models.Transaction.amount,
            models.Transaction.description,
            models.Category.name.label("category_name"),
        )
        .join(models.Category, models.Transaction.category_id == models.Category.id)
        .filter(models.Transaction.user_id == user_id)
        .filter(models.Category.type == "expense")
        .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
        .order_by(models.Transaction.transaction_date.asc(), models.Transaction.id.asc())
        .all()
    )

    if not tx_rows:
        return {
            "user_id": user_id,
            "month": month,
            "mean": 0.0,
            "std": 0.0,
            "z_threshold": z_threshold,
            "points": [],
        }

    amounts = [float(row.amount) for row in tx_rows]
    n = len(amounts)
    mean = sum(amounts) / n
    if n > 1:
        var = sum((x - mean) ** 2 for x in amounts) / (n - 1)
        std = sqrt(var)
    else:
        std = 0.0

    points: List[Dict] = []
    for row in tx_rows:
        amt = float(row.amount)
        if std > 0:
            z = (amt - mean) / std
        else:
            z = 0.0
        is_anomaly = abs(z) >= z_threshold
        points.append(
            {
                "id": row.id,
                "date": row.transaction_date,
                "amount": amt,
                "description": row.description,
                "category_name": row.category_name,
                "z_score": z,
                "is_anomaly": is_anomaly,
            }
        )

    return {
        "user_id": user_id,
        "month": month,
        "mean": mean,
        "std": std,
        "z_threshold": z_threshold,
        "points": points,
    }


    """
    Detect anomalous individual transactions using Z-score on transaction amounts.
    """
    tx_rows = (
        db.query(
            models.Transaction.id,
            models.Transaction.transaction_date,
            models.Transaction.amount,
            models.Transaction.description,
            models.Category.name.label("category_name"),
        )
        .join(models.Category, models.Transaction.category_id == models.Category.id)
        .filter(models.Transaction.user_id == user_id)
        .filter(models.Category.type == "expense")
        .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
        .order_by(models.Transaction.transaction_date.asc(), models.Transaction.id.asc())
        .all()
    )

    if not tx_rows:
        return {
            "user_id": user_id,
            "month": month,
            "mean": 0.0,
            "std": 0.0,
            "z_threshold": z_threshold,
            "points": [],
        }

    amounts = [float(row.amount) for row in tx_rows]
    n = len(amounts)
    mean = sum(amounts) / n
    if n > 1:
        var = sum((x - mean) ** 2 for x in amounts) / (n - 1)
        std = sqrt(var)
    else:
        std = 0.0

    points: List[Dict] = []
    for row in tx_rows:
        amt = float(row.amount)
        if std > 0:
            z = (amt - mean) / std
        else:
            z = 0.0
        is_anomaly = abs(z) >= z_threshold
        points.append(
            {
                "id": row.id,
                "date": row.transaction_date,
                "amount": amt,
                "description": row.description,
                "category_name": row.category_name,
                "z_score": z,
                "is_anomaly": is_anomaly,
            }
        )

    return {
        "user_id": user_id,
        "month": month,
        "mean": mean,
        "std": std,
        "z_threshold": z_threshold,
        "points": points,
    }

def build_daily_plot_series(
    db: Session,
    user_id: int,
    month: str,
    bands_sigma: float = 2.0,
) -> Dict:
    """
    Returns daily totals plus mean and upper/lower bands (mean ± kσ).
    Frontend / notebook can plot this easily.
    """
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
        .order_by(models.Transaction.transaction_date.asc())
        .all()
    )

    if not daily_rows:
        return {
            "user_id": user_id,
            "month": month,
            "mean": 0.0,
            "std": 0.0,
            "upper_band": 0.0,
            "lower_band": 0.0,
            "points": [],
        }

    totals = [float(row.total_amount) for row in daily_rows]
    n = len(totals)
    mean = sum(totals) / n
    if n > 1:
        var = sum((x - mean) ** 2 for x in totals) / (n - 1)
        std = sqrt(var)
    else:
        std = 0.0

    upper = mean + bands_sigma * std
    lower = max(0.0, mean - bands_sigma * std)

    points = [
        {"date": row.date, "total_amount": float(row.total_amount)}
        for row in daily_rows
    ]

    return {
        "user_id": user_id,
        "month": month,
        "mean": mean,
        "std": std,
        "upper_band": upper,
        "lower_band": lower,
        "points": points,
    }

def explain_anomalous_date(
    db: Session,
    user_id: int,
    date_str: str,
    z_threshold: float = 2.0,
) -> Tuple[str, str]:
    """
    Explain why a given date is anomalous (or not), using daily anomalies
    plus that day's transactions.
    """
    month = date_str[:7]
    summary = detect_daily_anomalies(db, user_id, month, z_threshold)
    points = summary.get("points", [])

    # find the given date
    day = None
    for p in points:
        if p["date"] == date_str:
            day = p
            break

    if not points:
        return (
            f"There is no expense data for user {user_id} in month {month}, "
            f"so I cannot analyze {date_str}.",
            "no_daily_data",
        )

    if day is None:
        return (
            f"There are no recorded expenses on {date_str} for user {user_id}.",
            "no_such_date",
        )

    total = day["total_amount"]
    z = day["z_score"]
    mean = summary["mean"]
    std = summary["std"]

    if not day["is_anomaly"]:
        # explain that it's not anomalous
        return (
            f"{date_str} is not flagged as anomalous. "
            f"You spent {total:.2f} on that day, compared to an average daily "
            f"spending of {mean:.2f} (z-score {z:.2f}, threshold {z_threshold:.2f}).",
            "not_anomaly",
        )

    # if anomalous, dig into that day's transactions
    tx_rows = (
        db.query(
            models.Transaction.transaction_date,
            models.Transaction.amount,
            models.Transaction.description,
            models.Category.name.label("category_name"),
        )
        .join(models.Category, models.Transaction.category_id == models.Category.id)
        .filter(models.Transaction.user_id == user_id)
        .filter(models.Category.type == "expense")
        .filter(models.Transaction.transaction_date == date_str)
        .order_by(models.Transaction.amount.desc())
        .all()
    )

    if not tx_rows:
        return (
            f"{date_str} is mathematically anomalous (z-score {z:.2f}), "
            f"but no individual transactions were found for that date.",
            "anomaly_no_tx_rows",
        )

    # group by category for explanation
    by_category: Dict[str, float] = {}
    for d, amt, desc, cat in tx_rows:
        by_category[cat] = by_category.get(cat, 0.0) + float(amt)

    cat_parts = [
        f"{cat}: {amount:.2f}" for cat, amount in sorted(
            by_category.items(), key=lambda kv: kv[1], reverse=True
        )
    ]
    cat_text = "; ".join(cat_parts)

    # optionally highlight a few largest descriptions
    top_descs = tx_rows[:3]
    desc_parts = []
    for d, amt, desc, cat in top_descs:
        desc_safe = desc or "(no description)"
        desc_parts.append(f"{desc_safe} ({cat}, {amt:.2f})")
    desc_text = "; ".join(desc_parts)

    explanation = (
        f"On {date_str}, you spent {total:.2f}, which is much higher than your "
        f"average daily spending of {mean:.2f} (z-score {z:.2f}, threshold {z_threshold:.2f}). "
        f"Most of this spending came from these categories: {cat_text}. "
        f"Some of the largest transactions were: {desc_text}."
    )

    return explanation, "is_anomaly"
