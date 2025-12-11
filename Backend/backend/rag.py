# # from __future__ import annotations

# # from dataclasses import dataclass
# # from datetime import datetime
# # from typing import List, Optional, Tuple

# # from sqlalchemy import func
# # from sqlalchemy.orm import Session

# # from . import models


# # @dataclass
# # class RAGContext:
# #     user_id: int
# #     month: str
# #     numeric_summary: str
# #     summary_text: str
# #     top_categories: List[tuple]  # list of (name, total)


# # # ==============
# # # Helper functions
# # # ==============

# # def _month_from_date_str(date_str: str) -> str:
# #     """Convert 'YYYY-MM-DD' -> 'YYYY-MM'."""
# #     return date_str[:7]


# # def _get_latest_month_for_user(db: Session, user_id: int) -> Optional[str]:
# #     """Return latest month (YYYY-MM) that has any transaction for user."""
# #     latest_date = (
# #         db.query(func.max(models.Transaction.transaction_date))
# #         .filter(models.Transaction.user_id == user_id)
# #         .scalar()
# #     )
# #     if not latest_date:
# #         return None
# #     return _month_from_date_str(latest_date)


# # # ==============
# # # Monthly summary (same DB logic as before)
# # # ==============

# # def build_monthly_summary(db: Session, user_id: int, month: str) -> models.MonthlySummary:
# #     """
# #     Compute numeric stats + a natural language summary for (user, month),
# #     store/update in monthly_summaries, and return the row.
# #     month must be 'YYYY-MM'.
# #     """
# #     # ----- total expenses -----
# #     total_spent = (
# #         db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0))
# #         .join(models.Category, models.Transaction.category_id == models.Category.id)
# #         .filter(models.Transaction.user_id == user_id)
# #         .filter(models.Category.type == "expense")
# #         .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
# #         .scalar()
# #     )

# #     # ----- total income -----
# #     total_income = (
# #         db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0))
# #         .join(models.Category, models.Transaction.category_id == models.Category.id)
# #         .filter(models.Transaction.user_id == user_id)
# #         .filter(models.Category.type == "income")
# #         .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
# #         .scalar()
# #     )

# #     # ----- top 3 categories -----
# #     top_categories = (
# #         db.query(
# #             models.Category.name,
# #             func.sum(models.Transaction.amount).label("total"),
# #         )
# #         .join(models.Category, models.Transaction.category_id == models.Category.id)
# #         .filter(models.Transaction.user_id == user_id)
# #         .filter(models.Category.type == "expense")
# #         .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
# #         .group_by(models.Category.id, models.Category.name)
# #         .order_by(func.sum(models.Transaction.amount).desc())
# #         .limit(3)
# #         .all()
# #     )

# #     if top_categories:
# #         top_cat_text_parts = [f"{name}: {total:.2f}" for name, total in top_categories]
# #         top_cat_text = "; ".join(top_cat_text_parts)
# #     else:
# #         top_cat_text = "No spending categories recorded."

# #     # ----- overspent categories vs budget -----
# #     overspent_rows = (
# #         db.query(
# #             models.Category.name,
# #             models.Budget.month,
# #             models.Budget.amount.label("budget_amount"),
# #             func.coalesce(func.sum(models.Transaction.amount), 0.0).label("actual_spent"),
# #         )
# #         .join(models.Category, models.Budget.category_id == models.Category.id)
# #         .outerjoin(
# #             models.Transaction,
# #             (models.Transaction.user_id == models.Budget.user_id)
# #             & (models.Transaction.category_id == models.Budget.category_id)
# #             & (func.substr(models.Transaction.transaction_date, 1, 7) == models.Budget.month),
# #         )
# #         .filter(models.Budget.user_id == user_id)
# #         .filter(models.Budget.month == month)
# #         .group_by(
# #             models.Category.name,
# #             models.Budget.month,
# #             models.Budget.amount,
# #         )
# #         .having(func.coalesce(func.sum(models.Transaction.amount), 0.0) > models.Budget.amount)
# #         .all()
# #     )

# #     if overspent_rows:
# #         over_text_parts = []
# #         for name, m, budget_amount, actual_spent in overspent_rows:
# #             over_text_parts.append(
# #                 f"{name}: spent {actual_spent:.2f} vs budget {budget_amount:.2f}"
# #             )
# #         overspent_text = "; ".join(over_text_parts)
# #     else:
# #         overspent_text = "No categories exceeded their budget."

# #     summary_lines = [
# #         f"Summary for {month}:",
# #         f"- Total expenses: {total_spent:.2f}",
# #         f"- Total income: {total_income:.2f}",
# #         f"- Top spending categories: {top_cat_text}",
# #         f"- Budget status: {overspent_text}",
# #     ]
# #     summary_text = "\n".join(summary_lines)

# #     # ----- upsert into MonthlySummary -----
# #     existing = (
# #         db.query(models.MonthlySummary)
# #         .filter(
# #             models.MonthlySummary.user_id == user_id,
# #             models.MonthlySummary.month == month,
# #         )
# #         .first()
# #     )

# #     now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

# #     if existing:
# #         existing.total_spent = float(total_spent)
# #         existing.total_income = float(total_income)
# #         existing.summary_text = summary_text
# #         existing.created_at = now_str
# #         summary = existing
# #     else:
# #         summary = models.MonthlySummary(
# #             user_id=user_id,
# #             month=month,
# #             total_spent=float(total_spent),
# #             total_income=float(total_income),
# #             summary_text=summary_text,
# #             created_at=now_str,
# #         )
# #         db.add(summary)

# #     db.commit()
# #     db.refresh(summary)
# #     return summary


# # # ==============
# # # Retrieval for RAG
# # # ==============

# # def _extract_month_from_question(
# #     db: Session, user_id: int, question: str
# # ) -> Tuple[Optional[str], str]:
# #     """
# #     Try to find YYYY-MM in the question; if none, use latest month with data.
# #     """
# #     import re

# #     q = question.lower()
# #     match = re.search(r"\d{4}-\d{2}", q)
# #     if match:
# #         return match.group(0), "month taken from question"

# #     latest = _get_latest_month_for_user(db, user_id)
# #     if latest:
# #         return latest, "month inferred as latest month with data"

# #     return None, "no month found and user has no data"


# # def retrieve_context(db: Session, user_id: int, question: str) -> Tuple[Optional[RAGContext], str]:
# #     """
# #     Core retrieval function. Stable interface for future models.
# #     """
# #     month, month_note = _extract_month_from_question(db, user_id, question)
# #     if not month:
# #         return None, month_note

# #     summary = build_monthly_summary(db, user_id, month)

# #     top_rows = (
# #         db.query(
# #             models.Category.name,
# #             func.sum(models.Transaction.amount).label("total"),
# #         )
# #         .join(models.Category, models.Transaction.category_id == models.Category.id)
# #         .filter(models.Transaction.user_id == user_id)
# #         .filter(models.Category.type == "expense")
# #         .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
# #         .group_by(models.Category.id, models.Category.name)
# #         .order_by(func.sum(models.Transaction.amount).desc())
# #         .all()
# #     )

# #     numeric_summary = (
# #         f"User {user_id}, month {month}: "
# #         f"total_spent={summary.total_spent:.2f}, "
# #         f"total_income={summary.total_income:.2f}"
# #     )

# #     ctx = RAGContext(
# #         user_id=user_id,
# #         month=month,
# #         numeric_summary=numeric_summary,
# #         summary_text=summary.summary_text or "",
# #         top_categories=top_rows,
# #     )
# #     return ctx, f"retrieval_ok; {month_note}"


# # # ==============
# # # Prompt + Ollama call
# # # ==============

# # def build_prompt(question: str, ctx: RAGContext) -> str:
# #     """
# #     Build a structured prompt for the model.
# #     """
# #     top_lines = [f"- {name}: {total:.2f}" for name, total in ctx.top_categories[:5]]
# #     top_block = "\n".join(top_lines) if top_lines else "No category breakdown available."

# #     prompt = f"""
# # You are an expense-tracking assistant for a single user.

# # You are given **trusted data from a database** for user {ctx.user_id} in month {ctx.month}.
# # You must base your answer ONLY on this data. If the user asks something about a different
# # month or something not present in the data, clearly say what you cannot answer and suggest
# # what you *can* answer instead.

# # Database context:

# # Numeric summary:
# # {ctx.numeric_summary}

# # Natural-language summary:
# # {ctx.summary_text}

# # Top spending categories (name: amount):
# # {top_block}

# # User question:
# # {question}

# # Instructions:
# # - Think about the numbers and relationships before answering.
# # - Mention the month {ctx.month} explicitly in your answer.
# # - Be concise (2–4 sentences).
# # - Do not invent data that is not implied by the context.
# # """
# #     return prompt.strip()


# # def call_ollama_chat(prompt: str, model: str = "llama3.2") -> str:
# #     """
# #     Call local Ollama (chat API) with the given prompt.
# #     Requires `ollama serve` running and `requests` installed.
# #     """
# #     import requests

# #     url = "http://localhost:11434/api/chat"
# #     payload = {
# #         "model": model,
# #         "messages": [
# #             {
# #                 "role": "system",
# #                 "content": (
# #                     "You are a precise budgeting assistant. "
# #                     "Use only the provided context from the database."
# #                 ),
# #             },
# #             {"role": "user", "content": prompt},
# #         ],
# #         "stream": False,
# #     }

# #     resp = requests.post(url, json=payload, timeout=120)
# #     resp.raise_for_status()
# #     data = resp.json()

# #     # Ollama chat response typically has: {"message": {"content": "..."}}
# #     message = data.get("message", {})
# #     content = message.get("content") or ""
# #     return content.strip()


# # # ==============
# # # Rule-based fallback (in case Ollama fails)
# # # ==============

# # def generate_answer_rule_based(question: str, ctx: RAGContext) -> str:
# #     q = question.lower()

# #     if "how much" in q and "spend" in q:
# #         # extract from numeric_summary string
# #         spent_part = ctx.numeric_summary.split("total_spent=")[1].split(",")[0]
# #         return f"In {ctx.month}, you spent a total of {spent_part}."

# #     if "income" in q:
# #         income_part = ctx.numeric_summary.split("total_income=")[1].split()[0]
# #         return f"In {ctx.month}, your recorded income was {income_part}."

# #     if "top" in q and "category" in q:
# #         if not ctx.top_categories:
# #             return f"In {ctx.month}, there are no expense categories recorded."
# #         best_name, best_total = ctx.top_categories[0]
# #         return f"In {ctx.month}, your top spending category was {best_name} with {best_total:.2f}."

# #     if "summary" in q or "overview" in q:
# #         return ctx.summary_text or f"No summary available for {ctx.month}."

# #     return (
# #         f"I can answer questions about your spending in {ctx.month} based on the database. "
# #         f"Key numbers are: {ctx.numeric_summary}. Try asking things like "
# #         f"'How much did I spend?', 'What was my top category?', or 'Give me a summary for {ctx.month}'."
# #     )


# # # ==============
# # # Public entrypoint used by FastAPI
# # # ==============

# # def answer_question(db: Session, user_id: int, question: str) -> Tuple[str, str]:
# #     """
# #     Main RAG entrypoint called from FastAPI.

# #     Returns: (answer, debug_info)
# #     """
# #     ctx, info = retrieve_context(db, user_id, question)
# #     if not ctx:
# #         return (
# #             "I could not find any transactions for this user yet, so I cannot answer the question.",
# #             f"retrieval_failed; {info}",
# #         )

# #     prompt = build_prompt(question, ctx)

# #     # Try Ollama first
# #     try:
# #         answer = call_ollama_chat(prompt)
# #         debug = f"{info}; engine=ollama"
# #         if not answer:
# #             raise RuntimeError("Empty answer from Ollama")
# #         return answer, debug
# #     except Exception as e:
# #         # Fallback to rule-based engine
# #         fallback = generate_answer_rule_based(question, ctx)
# #         debug = f"{info}; engine=rule_based; ollama_error={e}"
# #         return fallback, debug

# from __future__ import annotations

# from dataclasses import dataclass
# from datetime import datetime
# from typing import List, Optional, Tuple

# from sqlalchemy import func
# from sqlalchemy.orm import Session

# from . import models
# from .anomaly import explain_anomalous_date
# from .cluster import build_spending_feature_vector, cluster_user_profile_rule_based


# @dataclass
# class RAGContext:
#     user_id: int
#     user_name: str
#     user_email: str
#     month: str
#     numeric_summary: str
#     summary_text: str
#     top_categories: List[tuple]      # (category_name, total_amount)
#     transactions: List[tuple]        # (date, amount, description, category_name)


# # ==============
# # Helper functions
# # ==============

# def _month_from_date_str(date_str: str) -> str:
#     """Convert 'YYYY-MM-DD' or 'YYYY-MM-D' -> 'YYYY-MM'."""
#     return date_str[:7]

# def _extract_months_from_question(question: str) -> List[str]:
#     import re
#     # find all YYYY-MM patterns
#     return re.findall(r"\d{4}-\d{2}", question)

# def describe_segment_change(
#     db: Session, user_id: int, month1: str, month2: str
# ) -> str:
#     """
#     Compare user's spending segment between two months and describe change.
#     Uses rule-based segmentation on extended features.
#     """

#     feats1 = build_spending_feature_vector(db, user_id, month1)
#     seg1 = cluster_user_profile_rule_based(feats1)

#     feats2 = build_spending_feature_vector(db, user_id, month2)
#     seg2 = cluster_user_profile_rule_based(feats2)

#     label1 = seg1["label"]
#     label2 = seg2["label"]

#     # find dominant category both months
#     def dominant_category(features: Dict) -> str | None:
#         best_cat = None
#         best_ratio = -1.0
#         for name, r in features["ratios"].items():
#             if r > best_ratio:
#                 best_ratio = r
#                 best_cat = name
#         if best_ratio <= 0:
#             return None
#         return best_cat

#     dom1 = dominant_category(feats1)
#     dom2 = dominant_category(feats2)

#     parts = []
#     parts.append(
#         f"In {month1}, your spending segment was '{label1}', "
#         f"with a total of {feats1['grand_total']:.2f}."
#     )
#     if dom1:
#         parts.append(f"The dominant category was {dom1}.")

#     parts.append(
#         f"In {month2}, your spending segment is '{label2}', "
#         f"with a total of {feats2['grand_total']:.2f}."
#     )
#     if dom2:
#         parts.append(f"The dominant category is {dom2}.")

#     if label1 != label2 or dom1 != dom2:
#         parts.append(
#             "This means your spending pattern changed between the two months."
#         )
#     else:
#         parts.append(
#             "Overall, your spending pattern is quite similar between these two months."
#         )

#     return " ".join(parts)


# def _get_latest_month_for_user(db: Session, user_id: int) -> Optional[str]:
#     """Return latest month (YYYY-MM) that has any transaction for user."""
#     latest_date = (
#         db.query(func.max(models.Transaction.transaction_date))
#         .filter(models.Transaction.user_id == user_id)
#         .scalar()
#     )
#     if not latest_date:
#         return None
#     return _month_from_date_str(latest_date)

# def _is_cross_user_question(question: str) -> bool:
#     """
#     Detect obvious attempts to ask about other users / accounts.
#     This is a simple guard; data access is still limited by user_id in SQL.
#     """
#     q = question.lower()
#     bad_phrases = [
#         "other user",
#         "another user",
#         "someone else",
#         "other people",
#         "other account",
#         "other person",
#         "my friend’s account",
#         "friend's account",
#         "rcube",  # example name you mentioned
#     ]
#     return any(p in q for p in bad_phrases)



# # ==============
# # Monthly summary (same idea as before)
# # ==============

# def build_monthly_summary(db: Session, user_id: int, month: str) -> models.MonthlySummary:
#     """
#     Compute numeric stats + a natural language summary for (user, month),
#     store/update in monthly_summaries, and return the row.
#     month must be 'YYYY-MM'.
#     """
#     # ----- total expenses -----
#     total_spent = (
#         db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0))
#         .join(models.Category, models.Transaction.category_id == models.Category.id)
#         .filter(models.Transaction.user_id == user_id)
#         .filter(models.Category.type == "expense")
#         .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
#         .scalar()
#     )

#     # ----- total income -----
#     total_income = (
#         db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0))
#         .join(models.Category, models.Transaction.category_id == models.Category.id)
#         .filter(models.Transaction.user_id == user_id)
#         .filter(models.Category.type == "income")
#         .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
#         .scalar()
#     )

#     # ----- top 3 categories -----
#     top_categories = (
#         db.query(
#             models.Category.name,
#             func.sum(models.Transaction.amount).label("total"),
#         )
#         .join(models.Category, models.Transaction.category_id == models.Category.id)
#         .filter(models.Transaction.user_id == user_id)
#         .filter(models.Category.type == "expense")
#         .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
#         .group_by(models.Category.id, models.Category.name)
#         .order_by(func.sum(models.Transaction.amount).desc())
#         .limit(3)
#         .all()
#     )

#     if top_categories:
#         top_cat_text_parts = [f"{name}: {total:.2f}" for name, total in top_categories]
#         top_cat_text = "; ".join(top_cat_text_parts)
#     else:
#         top_cat_text = "No spending categories recorded."

#     # ----- overspent categories vs budget -----
#     overspent_rows = (
#         db.query(
#             models.Category.name,
#             models.Budget.month,
#             models.Budget.amount.label("budget_amount"),
#             func.coalesce(func.sum(models.Transaction.amount), 0.0).label("actual_spent"),
#         )
#         .join(models.Category, models.Budget.category_id == models.Category.id)
#         .outerjoin(
#             models.Transaction,
#             (models.Transaction.user_id == models.Budget.user_id)
#             & (models.Transaction.category_id == models.Budget.category_id)
#             & (func.substr(models.Transaction.transaction_date, 1, 7) == models.Budget.month),
#         )
#         .filter(models.Budget.user_id == user_id)
#         .filter(models.Budget.month == month)
#         .group_by(
#             models.Category.name,
#             models.Budget.month,
#             models.Budget.amount,
#         )
#         .having(func.coalesce(func.sum(models.Transaction.amount), 0.0) > models.Budget.amount)
#         .all()
#     )

#     if overspent_rows:
#         over_text_parts = []
#         for name, m, budget_amount, actual_spent in overspent_rows:
#             over_text_parts.append(
#                 f"{name}: spent {actual_spent:.2f} vs budget {budget_amount:.2f}"
#             )
#         overspent_text = "; ".join(over_text_parts)
#     else:
#         overspent_text = "No categories exceeded their budget."

#     summary_lines = [
#         f"Summary for {month}:",
#         f"- Total expenses: {total_spent:.2f}",
#         f"- Total income: {total_income:.2f}",
#         f"- Top spending categories: {top_cat_text}",
#         f"- Budget status: {overspent_text}",
#     ]
#     summary_text = "\n".join(summary_lines)

#     # ----- upsert into MonthlySummary -----
#     existing = (
#         db.query(models.MonthlySummary)
#         .filter(
#             models.MonthlySummary.user_id == user_id,
#             models.MonthlySummary.month == month,
#         )
#         .first()
#     )

#     now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

#     if existing:
#         existing.total_spent = float(total_spent)
#         existing.total_income = float(total_income)
#         existing.summary_text = summary_text
#         existing.created_at = now_str
#         summary = existing
#     else:
#         summary = models.MonthlySummary(
#             user_id=user_id,
#             month=month,
#             total_spent=float(total_spent),
#             total_income=float(total_income),
#             summary_text=summary_text,
#             created_at=now_str,
#         )
#         db.add(summary)

#     db.commit()
#     db.refresh(summary)
#     return summary


# # ==============
# # Retrieval for RAG
# # ==============

# def _extract_month_from_question(
#     db: Session, user_id: int, question: str
# ) -> Tuple[Optional[str], str]:
#     """
#     Try to find YYYY-MM in the question; if none, use latest month with data.
#     """
#     import re

#     q = question.lower()
#     match = re.search(r"\d{4}-\d{2}", q)
#     if match:
#         return match.group(0), "month taken from question"

#     latest = _get_latest_month_for_user(db, user_id)
#     if latest:
#         return latest, "month inferred as latest month with data"

#     return None, "no month found and user has no data"


# def retrieve_context(db: Session, user_id: int, question: str) -> Tuple[Optional[RAGContext], str]:
#     """
#     Core retrieval function. This is the main "R" in RAG.
#     Gathers:
#     - user info
#     - monthly summary
#     - top categories
#     - ALL transactions for that user & month (date, amount, description, category_name)
#     """
#     # Get month
#     month, month_note = _extract_month_from_question(db, user_id, question)
#     if not month:
#         return None, month_note

#     # User info
#     user = db.query(models.User).filter(models.User.id == user_id).first()
#     if not user:
#         return None, "user_not_found"

#     # Ensure monthly summary is up to date
#     summary = build_monthly_summary(db, user_id, month)

#     # Top categories for context
#     top_rows = (
#         db.query(
#             models.Category.name,
#             func.sum(models.Transaction.amount).label("total"),
#         )
#         .join(models.Category, models.Transaction.category_id == models.Category.id)
#         .filter(models.Transaction.user_id == user_id)
#         .filter(models.Category.type == "expense")
#         .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
#         .group_by(models.Category.id, models.Category.name)
#         .order_by(func.sum(models.Transaction.amount).desc())
#         .all()
#     )

#     # All transactions for that month for this user
#     tx_rows = (
#         db.query(
#             models.Transaction.transaction_date,
#             models.Transaction.amount,
#             models.Transaction.description,
#             models.Category.name.label("category_name"),
#         )
#         .join(models.Category, models.Transaction.category_id == models.Category.id)
#         .filter(models.Transaction.user_id == user_id)
#         .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
#         .order_by(models.Transaction.transaction_date.asc(), models.Transaction.id.asc())
#         .all()
#     )

#     numeric_summary = (
#         f"User {user_id}, month {month}: "
#         f"total_spent={summary.total_spent:.2f}, "
#         f"total_income={summary.total_income:.2f}"
#     )

#     ctx = RAGContext(
#         user_id=user_id,
#         user_name=user.name,
#         user_email=user.email,
#         month=month,
#         numeric_summary=numeric_summary,
#         summary_text=summary.summary_text or "",
#         top_categories=top_rows,
#         transactions=tx_rows,
#     )
#     return ctx, f"retrieval_ok; {month_note}"


# # ==============
# # Prompt + Ollama call
# # ==============

# def build_prompt(question: str, ctx: RAGContext) -> str:
#     """
#     Build a structured prompt for the model with full transaction context.
#     The model can now answer item-level questions like "Pizza" vs "Pasta".
#     """
#     top_lines = [f"- {name}: {total:.2f}" for name, total in ctx.top_categories[:5]]
#     top_block = "\n".join(top_lines) if top_lines else "No category breakdown available."

#     # Transaction table text
#     tx_lines = ["date | amount | description | category_name"]
#     for date, amount, desc, cat_name in ctx.transactions[:200]:  # limit rows for safety
#         desc_safe = desc or ""
#         tx_lines.append(f"{date} | {amount:.2f} | {desc_safe} | {cat_name}")
#     tx_block = "\n".join(tx_lines) if len(tx_lines) > 1 else "No transactions for this month."

#     prompt = f"""
# You are an expense-tracking assistant for a single user.

# You are given TRUSTED DATA from a database for user {ctx.user_id} in month {ctx.month}.
# You must base your answer ONLY on this data. DO NOT make up numbers.

# User profile:
# - Name: {ctx.user_name}
# - Email: {ctx.user_email}

# High-level numeric summary:
# {ctx.numeric_summary}

# Natural-language summary:
# {ctx.summary_text}

# Top spending categories (category: total_amount):
# {top_block}

# All transactions for this user and month (each row is one transaction):
# {tx_block}

# IMPORTANT:
# - The "description" column often contains item names like "Pizza", "Pasta", etc.
# - If the user asks about "Pizza", you MUST scan the transactions table and sum the amounts
#   of rows whose description contains the word "Pizza" (case-insensitive).
# - Likewise for other items.
# - If the user asks about total, categories, or budgets, use the numbers above.
# - If the user asks something outside this data (different month or unrelated), say clearly
#   what you cannot answer and suggest a valid question.

# User question:
# {question}

# Instructions for answering:
# - Think about the numbers and the transaction rows before answering.
# - Mention the month {ctx.month} explicitly in your answer.
# - Answer in 2–4 short sentences.
# - Do not invent any data that is not implied by the table.
# """
#     return prompt.strip()


# def call_ollama_chat(prompt: str, model: str = "llama3.2") -> str:
#     """
#     Call local Ollama (chat API) with the given prompt.
#     Requires `ollama serve` running and `requests` installed.
#     """
#     import requests

#     url = "http://localhost:11434/api/chat"
#     payload = {
#         "model": model,
#         "messages": [
#             {
#                 "role": "system",
#                 "content": (
#                     "You are a precise budgeting assistant. "
#                     "Use only the provided context from the database."
#                 ),
#             },
#             {"role": "user", "content": prompt},
#         ],
#         "stream": False,
#     }

#     resp = requests.post(url, json=payload, timeout=120)
#     resp.raise_for_status()
#     data = resp.json()

#     message = data.get("message", {})
#     content = message.get("content") or ""
#     return content.strip()


# # ==============
# # Rule-based fallback (exact calculations from DB context)
# # ==============

# def generate_answer_rule_based(question: str, ctx: RAGContext) -> str:
#     q = question.lower()

#     # Item-level total, e.g., "pizza", "pasta"
#     # Very simple extraction: look for single keywords
#     keywords = []
#     for word in ["pizza", "pasta", "coffee", "rent", "uber", "shopping"]:
#         if word in q:
#             keywords.append(word)

#     if keywords:
#         kw = keywords[0]  # just handle the first one found
#         total_kw = 0.0
#         for date, amount, desc, cat_name in ctx.transactions:
#             if desc and kw in desc.lower():
#                 total_kw += float(amount)
#         if total_kw > 0:
#             return (
#                 f"In {ctx.month}, your total spending on '{kw}' was {total_kw:.2f}, "
#                 f"based on the transaction descriptions."
#             )
#         else:
#             return (
#                 f"In {ctx.month}, I did not find any transactions whose description "
#                 f"contains '{kw}'."
#             )

#     # How much did I spend in this month?
#     if "how much" in q and "spend" in q:
#         spent_part = ctx.numeric_summary.split("total_spent=")[1].split(",")[0]
#         return f"In {ctx.month}, you spent a total of {spent_part}."

#     # Income
#     if "income" in q:
#         income_part = ctx.numeric_summary.split("total_income=")[1].split()[0]
#         return f"In {ctx.month}, your recorded income was {income_part}."

#     # Top category
#     if "top" in q and "category" in q:
#         if not ctx.top_categories:
#             return f"In {ctx.month}, there are no expense categories recorded."
#         best_name, best_total = ctx.top_categories[0]
#         return f"In {ctx.month}, your top spending category was {best_name} with {best_total:.2f}."

#     # Summary / overview
#     if "summary" in q or "overview" in q:
#         return ctx.summary_text or f"No summary available for {ctx.month}."

#     # Generic fallback
#     return (
#         f"I can answer questions about your spending in {ctx.month} based on the database. "
#         f"Key numbers are: {ctx.numeric_summary}. Try asking things like "
#         f"'How much did I spend?', 'What was my top category?', "
#         f"'What is my total Pizza spend?', or 'Give me a summary for {ctx.month}'."
#     )


# # ==============
# # Public entrypoint used by FastAPI
# # ==============

# # def answer_question(db: Session, user_id: int, question: str) -> Tuple[str, str]:
# #     """
# #     Main RAG entrypoint called from FastAPI.

# #     Returns: (answer, debug_info)
# #     """
# #     ctx, info = retrieve_context(db, user_id, question)
# #     if not ctx:
# #         return (
# #             "I could not find any transactions for this user yet, so I cannot answer the question.",
# #             f"retrieval_failed; {info}",
# #         )

# #     prompt = build_prompt(question, ctx)

# #     # Try Ollama first
# #     try:
# #         answer = call_ollama_chat(prompt)
# #         debug = f"{info}; engine=ollama"
# #         if not answer:
# #             raise RuntimeError("Empty answer from Ollama")
# #         return answer, debug
# #     except Exception as e:
# #         # Fallback to rule-based engine
# #         fallback = generate_answer_rule_based(question, ctx)
# #         debug = f"{info}; engine=rule_based; ollama_error={e}"
# #         return fallback, debug

# def _extract_full_date(question: str) -> Optional[str]:
#     import re
#     m = re.search(r"\d{4}-\d{2}-\d{2}", question)
#     if m:
#         return m.group(0)
#     return None


# def answer_question(db: Session, user_id: int, question: str) -> Tuple[str, str]:
#     """
#     Main RAG entrypoint called from FastAPI.

#     Returns: (answer, debug_info)
#     """
#      # 🔒 Privacy guard: refuse cross-user questions up-front
#     if _is_cross_user_question(question):
#         msg = (
#             "For privacy and security reasons, I can only show information for the "
#             "current user account. I cannot provide any details about other users "
#             "or their transactions."
#         )
#         return msg, "blocked_for_privacy"

#     # 🧠 Special case: anomaly explanation like “Why is 2025-12-03 anomalous?”
#     q_lower = question.lower()
#      # 🧠 Special case: compare segments between two months
#     months = _extract_months_from_question(question)
#     if len(months) >= 2 and ("compare" in q_lower or "difference" in q_lower or "change" in q_lower):
#         m1, m2 = months[0], months[1]
#         explanation = describe_segment_change(db, user_id, m1, m2)
#         return explanation, f"segment_compare; {m1}_vs_{m2}"
        
#     date_str = _extract_full_date(question)
#     if date_str and ("why" in q_lower or "anomal" in q_lower or "spike" in q_lower or "unusual" in q_lower):
#         explanation, dbg = explain_anomalous_date(db, user_id, date_str)
#         return explanation, f"anomaly_explain; date={date_str}; {dbg}"
    
#     if "cluster" in q_lower or "segment" in q_lower:
#         features = build_spending_feature_vector(db, user_id, month)
#         result = cluster_user_profile(features["vector"])
#         return f"You are in segment '{result['label']}'. This is because your spending pattern shows {explanation}."


#     ctx, info = retrieve_context(db, user_id, question)
#     if not ctx:
#         return (
#             "I could not find any transactions for this user yet, so I cannot answer the question.",
#             f"retrieval_failed; {info}",
#         )

#     prompt = build_prompt(question, ctx)

#     # Try Ollama first
#     try:
#         answer = call_ollama_chat(prompt)
#         debug = f"{info}; engine=ollama"
#         if not answer:
#             raise RuntimeError("Empty answer from Ollama")
#         return answer, debug
#     except Exception as e:
#         # Fallback to rule-based engine
#         fallback = generate_answer_rule_based(question, ctx)
#         debug = f"{info}; engine=rule_based; ollama_error={e}"
#         return fallback, debug


from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple, Dict

from sqlalchemy import func
from sqlalchemy.orm import Session

import models
from anomaly import explain_anomalous_date
from cluster import build_spending_feature_vector, cluster_user_profile_rule_based


@dataclass
class RAGContext:
    user_id: int
    user_name: str
    user_email: str
    month: str
    numeric_summary: str
    summary_text: str
    top_categories: List[tuple]      # (category_name, total_amount)
    transactions: List[tuple]        # (date, amount, description, category_name)


# =======================
# Helper functions
# =======================

def _month_from_date_str(date_str: str) -> str:
    """Convert 'YYYY-MM-DD' or 'YYYY-MM-D' -> 'YYYY-MM'."""
    return date_str[:7]


def _extract_months_from_question(question: str) -> List[str]:
    import re
    return re.findall(r"\d{4}-\d{2}", question)


def _extract_full_date(question: str) -> Optional[str]:
    import re
    m = re.search(r"\d{4}-\d{2}-\d{2}", question)
    if m:
        return m.group(0)
    return None


def _get_latest_month_for_user(db: Session, user_id: int) -> Optional[str]:
    latest_date = (
        db.query(func.max(models.Transaction.transaction_date))
        .filter(models.Transaction.user_id == user_id)
        .scalar()
    )
    if not latest_date:
        return None
    return _month_from_date_str(latest_date)


def _is_cross_user_question(question: str) -> bool:
    """
    Detect obvious attempts to ask about OTHER users / accounts.
    This is only a text-level guard; DB access is already filtered by user_id.
    """
    q = question.lower()
    bad_phrases = [
        "other user",
        "another user",
        "someone else",
        "other people",
        "other account",
        "other person",
        "my friend's account",
        "my friends account",
        "friend’s account",
    ]
    return any(p in q for p in bad_phrases)


def _user_display_name(user: models.User | None, user_id: int) -> str:
    if user is None:
        return f"User {user_id}"
    for attr in ("full_name", "name", "username"):
        if hasattr(user, attr) and getattr(user, attr):
            return str(getattr(user, attr))
    if getattr(user, "email", None):
        return str(user.email).split("@")[0]
    return f"User {user_id}"


def describe_segment_change(
    db: Session, user_id: int, month1: str, month2: str
) -> str:
    """
    Compare user's spending segment between two months and describe change.
    Uses rule-based segmentation on extended features.
    """
    feats1 = build_spending_feature_vector(db, user_id, month1)
    seg1 = cluster_user_profile_rule_based(feats1)

    feats2 = build_spending_feature_vector(db, user_id, month2)
    seg2 = cluster_user_profile_rule_based(feats2)

    label1 = seg1["label"]
    label2 = seg2["label"]

    def dominant_category(features: Dict) -> Optional[str]:
        best_cat = None
        best_ratio = -1.0
        for name, r in features.get("ratios", {}).items():
            if r > best_ratio:
                best_ratio = r
                best_cat = name
        if best_ratio <= 0:
            return None
        return best_cat

    dom1 = dominant_category(feats1)
    dom2 = dominant_category(feats2)

    parts: List[str] = []
    parts.append(
        f"In {month1}, your spending segment was '{label1}', "
        f"with a total of {feats1.get('grand_total', 0.0):.2f}."
    )
    if dom1:
        parts.append(f"The dominant category was {dom1}.")

    parts.append(
        f"In {month2}, your spending segment is '{label2}', "
        f"with a total of {feats2.get('grand_total', 0.0):.2f}."
    )
    if dom2:
        parts.append(f"The dominant category is {dom2}.")

    if label1 != label2 or dom1 != dom2:
        parts.append("This means your spending pattern changed between the two months.")
    else:
        parts.append("Overall, your spending pattern is quite similar between these months.")

    return " ".join(parts)


# =======================
# Monthly summary
# =======================

def build_monthly_summary(db: Session, user_id: int, month: str) -> models.MonthlySummary:
    """
    Compute numeric stats + a natural language summary for (user, month),
    store/update in monthly_summaries, and return the row.
    month must be 'YYYY-MM'.
    """
    total_spent = (
        db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0))
        .join(models.Category, models.Transaction.category_id == models.Category.id)
        .filter(models.Transaction.user_id == user_id)
        .filter(models.Category.type == "expense")
        .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
        .scalar()
    )

    total_income = (
        db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0))
        .join(models.Category, models.Transaction.category_id == models.Category.id)
        .filter(models.Transaction.user_id == user_id)
        .filter(models.Category.type == "income")
        .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
        .scalar()
    )

    # Net savings (income minus absolute expenses)
    net_savings = float(total_income) - abs(float(total_spent))

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

    if top_categories:
        top_cat_text_parts = [f"{name}: {total:.2f}" for name, total in top_categories]
        top_cat_text = "; ".join(top_cat_text_parts)
    else:
        top_cat_text = "No spending categories recorded."

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
            & (func.substr(models.Transaction.transaction_date, 1, 7) == models.Budget.month),
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

    summary_lines = [
        f"Summary for {month}:",
        f"- Total expenses: {abs(float(total_spent)):.2f}",
        f"- Total income: {float(total_income):.2f}",
        f"- Net savings: {net_savings:.2f}",
        f"- Top spending categories: {top_cat_text}",
        f"- Budget status: {overspent_text}",
    ]
    summary_text = "\n".join(summary_lines)

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


# =======================
# Retrieval for RAG
# =======================

def _extract_months_from_question(question: str) -> List[str]:
    """
    Extract month(s) from a natural-language question in a few formats:
    - '2025-12'
    - '12-2025'
    - 'december 2025', 'Dec 2025', etc.

    Always return normalized strings 'YYYY-MM'.
    """
    import re

    q = question.lower()
    months: List[str] = []

    # 1) YYYY-MM (e.g., 2025-12)
    for year, mm in re.findall(r"\b(\d{4})-(\d{2})\b", q):
        value = f"{year}-{mm}"
        if value not in months:
            months.append(value)

    # 2) MM-YYYY (e.g., 12-2025)  -> normalize to YYYY-MM
    for mm, year in re.findall(r"\b(\d{2})-(\d{4})\b", q):
        value = f"{year}-{mm}"
        if value not in months:
            months.append(value)

    # 3) Month name + year (e.g., "december 2025", "Dec 2025")
    month_map = {
        "january": "01",
        "jan": "01",
        "february": "02",
        "feb": "02",
        "march": "03",
        "mar": "03",
        "april": "04",
        "apr": "04",
        "may": "05",
        "june": "06",
        "jun": "06",
        "july": "07",
        "jul": "07",
        "august": "08",
        "aug": "08",
        "september": "09",
        "sep": "09",
        "sept": "09",
        "october": "10",
        "oct": "10",
        "november": "11",
        "nov": "11",
        "december": "12",
        "dec": "12",
    }

    for name, mm in month_map.items():
        # e.g. "december 2025", "dec 2025"
        pattern = rf"\b{name}\s+(\d{{4}})\b"
        for year in re.findall(pattern, q):
            value = f"{year}-{mm}"
            if value not in months:
                months.append(value)

    return months

def _extract_month_from_question(
    db: Session, user_id: int, question: str
) -> Tuple[Optional[str], str]:
    """
    Try to infer a single month (YYYY-MM) from the question.

    Priority:
    1) Any month detected in the text (2025-12, 12-2025, 'december 2025', ...)
    2) Otherwise, fall back to the latest month that has data for this user.
    """
    months = _extract_months_from_question(question)
    if months:
        # If user mentioned multiple months, just use the first one here.
        # (The multi-month compare logic uses _extract_months_from_question directly.)
        return months[0], "month taken from question"

    latest = _get_latest_month_for_user(db, user_id)
    if latest:
        return latest, "month inferred as latest month with data"

    return None, "no month found and user has no data"


def retrieve_context(db: Session, user_id: int, question: str) -> Tuple[Optional[RAGContext], str]:
    month, month_note = _extract_month_from_question(db, user_id, question)
    if not month:
        return None, month_note

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None, "user_not_found"

    summary = build_monthly_summary(db, user_id, month)

    top_rows = (
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
        .all()
    )

    tx_rows = (
        db.query(
            models.Transaction.transaction_date,
            models.Transaction.amount,
            models.Transaction.description,
            models.Category.name.label("category_name"),
        )
        .join(models.Category, models.Transaction.category_id == models.Category.id)
        .filter(models.Transaction.user_id == user_id)
        .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
        .order_by(models.Transaction.transaction_date.asc(), models.Transaction.id.asc())
        .all()
    )

    net_savings = summary.total_income - abs(summary.total_spent)
    numeric_summary = (
        f"User {user_id}, month {month}: "
        f"total_spent={abs(summary.total_spent):.2f}, "
        f"total_income={summary.total_income:.2f}, "
        f"net_savings={net_savings:.2f}"
    )

    ctx = RAGContext(
        user_id=user_id,
        user_name=_user_display_name(user, user_id),
        user_email=user.email if getattr(user, "email", None) else "",
        month=month,
        numeric_summary=numeric_summary,
        summary_text=summary.summary_text or "",
        top_categories=top_rows,
        transactions=tx_rows,
    )
    return ctx, f"retrieval_ok; {month_note}"


# =======================
# Prompt + Ollama call
# =======================

def build_prompt(question: str, ctx: RAGContext) -> str:
    top_lines = [f"- {name}: {total:.2f}" for name, total in ctx.top_categories[:5]]
    top_block = "\n".join(top_lines) if top_lines else "No category breakdown available."

    tx_lines = ["date | amount | description | category_name"]
    for date, amount, desc, cat_name in ctx.transactions[:200]:
        desc_safe = desc or ""
        tx_lines.append(f"{date} | {amount:.2f} | {desc_safe} | {cat_name}")
    tx_block = "\n".join(tx_lines) if len(tx_lines) > 1 else "No transactions for this month."

    prompt = f"""
You are **Rcube**, an AI expense assistant for a single user.

User:
- id: {ctx.user_id}
- name: {ctx.user_name}
- email: {ctx.user_email}

You are given TRUSTED DATA from a database for this user in month {ctx.month}.
You must base your answer ONLY on this data. DO NOT make up numbers.

High-level numeric summary:
{ctx.numeric_summary}

Natural-language summary:
{ctx.summary_text}

Top spending categories (category: total_amount):
{top_block}

All transactions for this user and month (each row is one transaction):
{tx_block}

IMPORTANT BEHAVIOR RULES:
- FIRST, read the user's question carefully.
- If the question is about greetings or something very general (not directly
  asking about money, spending, income, categories, budgets, anomalies, or
  segments), give a short friendly answer and explain briefly what you can do.
  Do NOT list totals or category amounts in that case.
- If the question *is* about spending, budgets, anomalies, categories, or
  segments, then use the data above to compute the answer as precisely as you can.
- Only mention totals, categories, or specific transactions that are directly
  relevant to answering the question.
- Never invent values that are not implied by the data.

Transaction hints:
- The "description" column often contains item names like "Pizza", "Pasta", etc.
- If the user asks about "Pizza", scan the transactions table and sum the amounts
  of rows whose description contains the word "Pizza" (case-insensitive).

Answering style:
- Start your answer by addressing the user by name (e.g., "Hi {ctx.user_name}, ...").
- Keep the answer in 2-5 short sentences or concise bullet points.
- If the question cannot be answered from this data, say so clearly and suggest
  what you *can* answer instead (e.g., totals, top category, anomalies).

User question:
{question}
"""
    return prompt.strip()



def call_ollama_chat(prompt: str, model: str = "llama3.2") -> str:
    import requests

    url = "http://localhost:11434/api/chat"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a precise, privacy-preserving budgeting assistant. "
                    "Use only the provided context from the database."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "stream": False,
    }

    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    message = data.get("message", {})
    content = message.get("content") or ""
    return content.strip()


# =======================
# Rule-based fallback
# =======================

def generate_answer_rule_based(question: str, ctx: RAGContext) -> str:
    q = question.lower()

    # Simple keyword-based item totals
    keywords = []
    for word in ["pizza", "pasta", "coffee", "rent", "uber", "shopping"]:
        if word in q:
            keywords.append(word)

    if keywords:
        kw = keywords[0]
        total_kw = 0.0
        for date, amount, desc, cat_name in ctx.transactions:
            if desc and kw in desc.lower():
                total_kw += float(amount)
        if total_kw > 0:
            return (
                f"In {ctx.month}, your total spending on '{kw}' was {total_kw:.2f}, "
                f"based on the transaction descriptions."
            )
        else:
            return (
                f"In {ctx.month}, I did not find any transactions whose description "
                f"contains '{kw}'."
            )

    if "how much" in q and "spend" in q:
        spent_part = ctx.numeric_summary.split("total_spent=")[1].split(",")[0]
        return f"In {ctx.month}, you spent a total of {spent_part}."

    if "income" in q:
        income_part = ctx.numeric_summary.split("total_income=")[1].split(",")[0]
        return f"In {ctx.month}, your recorded income was {income_part}."

    if "saving" in q or "savings" in q or "net" in q:
        # numeric_summary contains net_savings=...
        try:
            net_part = ctx.numeric_summary.split("net_savings=")[1].split()[0]
        except Exception:
            net_part = "N/A"
        return (
            f"In {ctx.month}, your net savings (income minus expenses) were {net_part}. "
            f"Income: {ctx.numeric_summary.split('total_income=')[1].split(',')[0]}, "
            f"Expenses: {ctx.numeric_summary.split('total_spent=')[1].split(',')[0]}."
        )

    if "top" in q and "category" in q:
        if not ctx.top_categories:
            return f"In {ctx.month}, there are no expense categories recorded."
        best_name, best_total = ctx.top_categories[0]
        return f"In {ctx.month}, your top spending category was {best_name} with {best_total:.2f}."

    if "summary" in q or "overview" in q:
        return ctx.summary_text or f"No summary available for {ctx.month}."

    return (
        f"I can answer questions about your spending in {ctx.month} based on the database. "
        f"Key numbers are: {ctx.numeric_summary}. Try asking things like "
        f"'How much did I spend?', 'What was my top category?', or "
        f"'What is my total Pizza spend in {ctx.month}?'."
    )


# =======================
# Public entrypoint for FastAPI
# =======================

def answer_question(db: Session, user_id: int, question: str) -> Tuple[str, str]:
    """
    Main RAG entrypoint called from FastAPI.

    Returns: (answer, debug_info)
    """

    # Normalize the text once
    q_stripped = question.strip()
    q_lower = q_stripped.lower()

    # -----------------------------
    # 🟢 1) Handle simple greetings
    # -----------------------------
    greeting_words = ["hi", "hii", "hiii", "hello", "hey", "hola", "namaste"]

    is_simple_greeting = (
        q_lower in greeting_words
        or any(q_lower.startswith(w + " ") for w in greeting_words)
    )

    if is_simple_greeting:
        # We only need the user name for a nice greeting
        user = db.query(models.User).filter(models.User.id == user_id).first()
        name = _user_display_name(user, user_id)

        msg = (
            f"Hi {name}, I’m Rcube, your personal finance assistant. "
            "You can ask me things like:\n"
            "- \"How much did I spend on Pizza in 2025-12?\"\n"
            "- \"What was my top category this month?\"\n"
            "- \"Why was 2025-12-03 flagged as an anomaly?\""
        )
        return msg, "greeting_only"

    # -----------------------------
    # 🔒 2) Privacy guard
    # -----------------------------
    if _is_cross_user_question(question):
        msg = (
            "For privacy and security reasons, I can only show information for your own "
            "account, not other users."
        )
        return msg, "blocked_for_privacy"

    # Reuse lowercased version for the rest
    q_lower = q_stripped.lower()
    months = _extract_months_from_question(question)

    # -----------------------------
    # 🧠 3) Segment comparison: "compare 2025-12 and 2026-01"
    # -----------------------------
    if len(months) >= 2 and (
        "compare" in q_lower or "difference" in q_lower or "change" in q_lower
    ):
        m1, m2 = months[0], months[1]
        explanation = describe_segment_change(db, user_id, m1, m2)
        return explanation, f"segment_compare; {m1}_vs_{m2}"

    # -----------------------------
    # 🧠 4) Anomaly explanation: "why is 2025-12-03 anomalous?"
    # -----------------------------
    date_str = _extract_full_date(question)
    if date_str and ("why" in q_lower or "anomal" in q_lower or "spike" in q_lower or "unusual" in q_lower):
        explanation, dbg = explain_anomalous_date(db, user_id, date_str)
        return explanation, f"anomaly_explain; date={date_str}; {dbg}"

    # -----------------------------
    # 🧠 5) Single-month segment: "what is my segment in 2025-12?"
    # -----------------------------
    if "cluster" in q_lower or "segment" in q_lower or "spending profile" in q_lower:
        if months:
            month = months[0]
        else:
            month = _get_latest_month_for_user(db, user_id)
        if not month:
            return (
                "I don't yet have enough data to build your spending segment.",
                "no_data_for_cluster",
            )
        feats = build_spending_feature_vector(db, user_id, month)
        seg = cluster_user_profile_rule_based(feats)
        label = seg.get("label", "Unknown segment")

        dominant = None
        ratios = feats.get("ratios", {})
        if ratios:
            dominant = max(ratios.items(), key=lambda kv: kv[1])[0]

        extra = f" Your dominant category is {dominant}." if dominant else ""
        return (
            f"In {month}, your spending segment is '{label}'.{extra}",
            f"segment_single; month={month}",
        )

    # -----------------------------
    # 🧠 6) Default: full RAG + Ollama
    # -----------------------------
    ctx, info = retrieve_context(db, user_id, question)
    if not ctx:
        return (
            "I could not find any transactions for you yet, so I cannot answer that question.",
            f"retrieval_failed; {info}",
        )

    prompt = build_prompt(question, ctx)

    try:
        answer = call_ollama_chat(prompt)
        debug = f"{info}; engine=ollama"
        if not answer:
            raise RuntimeError("Empty answer from Ollama")
        return answer, debug
    except Exception as e:
        fallback = generate_answer_rule_based(question, ctx)
        debug = f"{info}; engine=rule_based; ollama_error={e}"
        return fallback, debug

