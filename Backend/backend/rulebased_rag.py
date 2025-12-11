from __future__ import annotations

from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

import models


def _month_from_date_str(date_str: str) -> str:
    """
    Convert 'YYYY-MM-DD' -> 'YYYY-MM'.
    Assumes valid string; used only with DB values.
    """
    return date_str[:7]


def _get_latest_month_for_user(db: Session, user_id: int) -> Optional[str]:
    """Return latest month (YYYY-MM) that has any transaction for user."""
    latest_date = (
        db.query(func.max(models.Transaction.transaction_date))
        .filter(models.Transaction.user_id == user_id)
        .scalar()
    )
    if not latest_date:
        return None
    return _month_from_date_str(latest_date)


def build_monthly_summary(
    db: Session, user_id: int, month: str
) -> models.MonthlySummary:
    """
    Compute numeric stats + a natural language summary for (user, month),
    store/update in monthly_summaries, and return the row.
    month must be 'YYYY-MM'.
    """
    # ---------- total spent ----------
    total_spent = (
        db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0))
        .join(models.Category, models.Transaction.category_id == models.Category.id)
        .filter(models.Transaction.user_id == user_id)
        .filter(models.Category.type == "expense")
        .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
        .scalar()
    )

    # ---------- total income (if any) ----------
    total_income = (
        db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0))
        .join(models.Category, models.Transaction.category_id == models.Category.id)
        .filter(models.Transaction.user_id == user_id)
        .filter(models.Category.type == "income")
        .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
        .scalar()
    )

    # ---------- net savings (income minus absolute expenses) ----------
    net_savings = float(total_income) - abs(float(total_spent))

    # ---------- top 3 categories ----------
    top_categories = (
        db.query(
            models.Category.name,
            func.sum(models.Transaction.amount).label("total"),
        )
        .join(models.Category, models.Transaction.category_id == models.Category.id)
        .filter(models.Transaction.user_id == user_id)
        .filter(models.Category.type == "expense")
        .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
        .group_by(models.Category.id, models.Category.name)
        .order_by(func.sum(models.Transaction.amount).desc())
        .limit(3)
        .all()
    )

    top_cat_text_parts = []
    for name, total in top_categories:
        top_cat_text_parts.append(f"{name}: {total:.2f}")
    if top_cat_text_parts:
        top_cat_text = "; ".join(top_cat_text_parts)
    else:
        top_cat_text = "No spending categories recorded."

    # ---------- overspent categories vs budget ----------
    overspent_rows = (
        db.query(
            models.Category.name,
            models.Budget.month,
            models.Budget.amount.label("budget_amount"),
            func.coalesce(func.sum(models.Transaction.amount), 0.0).label("actual_spent"),
        )
        .join(models.Category, models.Budget.category_id == models.Category.id)
        .outerjoin(
            models.Transaction,
            (models.Transaction.user_id == models.Budget.user_id)
            & (models.Transaction.category_id == models.Budget.category_id)
            & (
                func.substr(models.Transaction.transaction_date, 1, 7)
                == models.Budget.month
            ),
        )
        .filter(models.Budget.user_id == user_id)
        .filter(models.Budget.month == month)
        .group_by(
            models.Category.name,
            models.Budget.month,
            models.Budget.amount,
        )
        .having(func.coalesce(func.sum(models.Transaction.amount), 0.0) > models.Budget.amount)
        .all()
    )

    if overspent_rows:
        over_text_parts = []
        for name, m, budget_amount, actual_spent in overspent_rows:
            over_text_parts.append(
                f"{name}: spent {actual_spent:.2f} vs budget {budget_amount:.2f}"
            )
        overspent_text = "; ".join(over_text_parts)
    else:
        overspent_text = "No categories exceeded their budget."

    # ---------- build natural language summary ----------
    summary_lines = [
        f"Summary for {month}:",
        f"- Total expenses: {abs(float(total_spent)):.2f}",
        f"- Total income: {float(total_income):.2f}",
        f"- Net savings: {net_savings:.2f}",
        f"- Top spending categories: {top_cat_text}",
        f"- Budget status: {overspent_text}",
    ]
    summary_text = "\n".join(summary_lines)

    # ---------- upsert into MonthlySummary ----------
    existing = (
        db.query(models.MonthlySummary)
        .filter(
            models.MonthlySummary.user_id == user_id,
            models.MonthlySummary.month == month,
        )
        .first()
    )

    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    if existing:
        existing.total_spent = float(total_spent)
        existing.total_income = float(total_income)
        existing.summary_text = summary_text
        existing.created_at = now_str
        summary = existing
    else:
        summary = models.MonthlySummary(
            user_id=user_id,
            month=month,
            total_spent=float(total_spent),
            total_income=float(total_income),
            summary_text=summary_text,
            created_at=now_str,
        )
        db.add(summary)

    db.commit()
    db.refresh(summary)
    return summary


def _extract_month_from_question(
    db: Session, user_id: int, question: str
) -> Tuple[Optional[str], str]:
    """
    Try to find YYYY-MM in the question.
    If none, fall back to latest month with data.
    Returns (month, debug_note).
    """
    import re

    match = re.search(r"\d{4}-\d{2}", question)
    if match:
        return match.group(0), "month taken from question"

    latest = _get_latest_month_for_user(db, user_id)
    if latest:
        return latest, "month inferred as latest month with data"

    return None, "no month found and user has no data"


def answer_question(db: Session, user_id: int, question: str) -> Tuple[str, str]:
    """
    Very simple 'RAG-style' router:
    - chooses intent from question text
    - ensures monthly summary exists
    - returns text answer + debug info
    """
    q_lower = question.lower().strip()

    month, month_note = _extract_month_from_question(db, user_id, q_lower)
    if not month:
        return (
            "I could not find any transactions for this user yet, so I cannot answer the question.",
            month_note,
        )

    # Make sure summary exists
    summary = build_monthly_summary(db, user_id, month)

    # --- intent: ask for full summary ---
    if "summary" in q_lower or "overview" in q_lower:
        return summary.summary_text or "No summary text available.", f"intent=summary; {month_note}"

    # --- intent: total spent ---
    if ("how much" in q_lower and "spend" in q_lower) or "expense" in q_lower:
        ans = (
            f"In {month}, you spent a total of {abs(summary.total_spent):.2f} "
            f"and your income was {summary.total_income:.2f}."
        )
        return ans, f"intent=total_spent; {month_note}"

    # --- intent: savings ---
    if "saving" in q_lower or "savings" in q_lower or "net" in q_lower:
        net_savings = summary.total_income - abs(summary.total_spent)
        ans = (
            f"In {month}, your net savings (income minus expenses) are {net_savings:.2f}. "
            f"Income: {summary.total_income:.2f}, Expenses: {abs(summary.total_spent):.2f}."
        )
        return ans, f"intent=net_savings; {month_note}"

    # --- intent: budget / over budget ---
    if "budget" in q_lower or "over budget" in q_lower:
        # Rebuild overspent text using same logic as above
        # (simpler: just reuse summary text line that already has overspent info)
        lines = (summary.summary_text or "").splitlines()
        budget_line = next((ln for ln in lines if "Budget status" in ln), None)
        if not budget_line:
            budget_line = "Budget status not available."
        return budget_line, f"intent=budget_status; {month_note}"

    # Fallback: return generic summary
    return summary.summary_text or "No summary text available.", f"intent=fallback_summary; {month_note}"
