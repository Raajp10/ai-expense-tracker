from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .db import engine, Base, get_db
from . import models, schemas

from .rag import build_monthly_summary, answer_question
from .cluster import build_spending_feature_vector, cluster_user_profile
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from sqlalchemy import func






from .anomaly import (
    detect_daily_anomalies,
    detect_daily_anomalies_by_category,
    detect_transaction_anomalies,
    build_daily_plot_series,
)

from .cluster import (
    build_spending_feature_vector,
    cluster_user_profile_rule_based,
    global_kmeans_clusters,
    global_gmm_clusters,
)


# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Expense Tracker Backend - Step 3")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],   # GET, POST, OPTIONS, etc.
    allow_headers=["*"],
)


# ---------- Helper ----------

def now_str() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


# ---------- Users ----------

@app.post("/users/", response_model=schemas.UserOut)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # Very simple "hash": in real life, use bcrypt/argon2
    password_hash = f"plain::{user_in.password}"

    user = models.User(
        name=user_in.name,
        email=user_in.email,
        password_hash=password_hash,
        created_at=now_str(),
    )
    db.add(user)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")
    db.refresh(user)
    return user


@app.get("/users/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users/", response_model=list[schemas.UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


# ---------- Categories ----------

@app.post("/categories/", response_model=schemas.CategoryOut)
def create_category(cat_in: schemas.CategoryCreate, db: Session = Depends(get_db)):
    if cat_in.type not in ("expense", "income"):
        raise HTTPException(status_code=400, detail="type must be 'expense' or 'income'")

    user = db.query(models.User).filter(models.User.id == cat_in.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    category = models.Category(
        user_id=cat_in.user_id,
        name=cat_in.name,
        type=cat_in.type,
        created_at=now_str(),
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@app.get("/categories/", response_model=list[schemas.CategoryOut])
def list_categories(user_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(models.Category)
    if user_id is not None:
        q = q.filter(models.Category.user_id == user_id)
    return q.all()


# ---------- Transactions ----------

@app.post("/transactions/", response_model=schemas.TransactionOut)
def create_transaction(tx_in: schemas.TransactionCreate, db: Session = Depends(get_db)):
    # Basic checks
    user = db.query(models.User).filter(models.User.id == tx_in.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    category = db.query(models.Category).filter(
        models.Category.id == tx_in.category_id,
        models.Category.user_id == tx_in.user_id,
    ).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found for this user")

    tx = models.Transaction(
        user_id=tx_in.user_id,
        category_id=tx_in.category_id,
        amount=tx_in.amount,
        transaction_date=tx_in.transaction_date,
        description=tx_in.description,
        created_at=now_str(),
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


@app.get("/transactions/", response_model=list[schemas.TransactionOut])
def list_transactions(
    user_id: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(models.Transaction)
        .filter(models.Transaction.user_id == user_id)
        .order_by(models.Transaction.transaction_date.desc())
        .all()
    )


# ---------- Budgets ----------

@app.post("/budgets/", response_model=schemas.BudgetOut)
def create_budget(b_in: schemas.BudgetCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == b_in.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    category = db.query(models.Category).filter(
        models.Category.id == b_in.category_id,
        models.Category.user_id == b_in.user_id,
    ).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found for this user")

    budget = models.Budget(
        user_id=b_in.user_id,
        category_id=b_in.category_id,
        month=b_in.month,
        amount=b_in.amount,
        created_at=now_str(),
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


@app.get("/budgets/", response_model=list[schemas.BudgetOut])
def list_budgets(
    user_id: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(models.Budget)
        .filter(models.Budget.user_id == user_id)
        .order_by(models.Budget.month.desc())
        .all()
    )

# ---------- Monthly summaries (for RAG) ----------

@app.post("/summaries/build", response_model=schemas.MonthlySummaryOut)
def api_build_summary(
    req: schemas.BuildSummaryRequest,
    db: Session = Depends(get_db),
):
    # verify user exists
    user = db.query(models.User).filter(models.User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    summary = build_monthly_summary(db, req.user_id, req.month)
    return summary


@app.get("/summaries/{user_id}", response_model=list[schemas.MonthlySummaryOut])
def api_list_summaries(user_id: int, db: Session = Depends(get_db)):
    summaries = (
        db.query(models.MonthlySummary)
        .filter(models.MonthlySummary.user_id == user_id)
        .order_by(models.MonthlySummary.month.desc())
        .all()
    )
    return summaries


# ---------- RAG-style Q&A endpoint ----------

@app.post("/rag/ask", response_model=schemas.QAResponse)
def api_rag_ask(req: schemas.QARequest, db: Session = Depends(get_db)):
    # verify user exists
    user = db.query(models.User).filter(models.User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    answer, debug = answer_question(db, req.user_id, req.question)
    return schemas.QAResponse(answer=answer, debug=debug)

# ---------- Step 7: Daily Anomaly Detection (Z-score) ----------

@app.post("/anomalies/daily", response_model=schemas.DetectDailyAnomaliesResponse)
def api_detect_daily_anomalies(
    req: schemas.DetectDailyAnomaliesRequest,
    db: Session = Depends(get_db),
):
    # Safety: verify user exists
    user = db.query(models.User).filter(models.User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result_dict = detect_daily_anomalies(
        db=db,
        user_id=req.user_id,
        month=req.month,
        z_threshold=req.z_threshold,
    )
    # Pydantic will validate/convert the dict to DetectDailyAnomaliesResponse
    return result_dict

# ---------- Step 7 extended: per-category, tx-level, plot ----------

@app.post("/anomalies/daily/by-category", response_model=schemas.DetectDailyAnomaliesResponse)
def api_detect_daily_anomalies_by_category(
    req: schemas.DetectDailyAnomaliesByCategoryRequest,
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result_dict = detect_daily_anomalies_by_category(
        db=db,
        user_id=req.user_id,
        month=req.month,
        category_name=req.category_name,
        z_threshold=req.z_threshold,
    )
    return result_dict


@app.post("/anomalies/transactions", response_model=schemas.DetectTransactionAnomaliesResponse)
def api_detect_transaction_anomalies(
    req: schemas.DetectTransactionAnomaliesRequest,
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result_dict = detect_transaction_anomalies(
        db=db,
        user_id=req.user_id,
        month=req.month,
        z_threshold=req.z_threshold,
    )
    return result_dict


@app.post("/anomalies/daily/plot", response_model=schemas.DailyPlotSeriesResponse)
def api_daily_plot_series(
    req: schemas.DetectDailyAnomaliesRequest,
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result_dict = build_daily_plot_series(
        db=db,
        user_id=req.user_id,
        month=req.month,
        bands_sigma=req.z_threshold,
    )
    return result_dict

@app.post("/cluster/segments", response_model=schemas.ClusterResponse)
def api_cluster_segments(
    req: schemas.ClusterRequest,
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    features = build_spending_feature_vector(db, req.user_id, req.month)
    result = cluster_user_profile(features)

    return {
        "user_id": req.user_id,
        "month": req.month,
        "cluster_id": result["cluster_id"],
        "label": result["label"],
        "centroid": result["centroid"],
        "categories": features["categories"],
        "totals": features["totals"],
        "ratios": features["ratios"],
    }

@app.post("/cluster/segments", response_model=schemas.ClusterResponse)
def api_cluster_segments(
    req: schemas.ClusterRequest,
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    features = build_spending_feature_vector(db, req.user_id, req.month)
    result = cluster_user_profile_rule_based(features)

    return {
        "user_id": req.user_id,
        "month": req.month,
        "cluster_id": result["cluster_id"],
        "label": result["label"],
        "centroid": result["centroid"],
        "categories": features["categories"],
        "totals": features["totals"],
        "ratios": features["ratios"],
    }

@app.post("/cluster/global", response_model=schemas.GlobalClusterResponse)
def api_global_clusters(
    req: schemas.GlobalClusterRequest,
    db: Session = Depends(get_db),
):
    if req.algo.lower() == "kmeans":
        mapping = global_kmeans_clusters(db, req.month, n_clusters=req.n_clusters)
        algo_name = "kmeans"
    else:
        mapping = global_gmm_clusters(db, req.month, n_components=req.n_clusters)
        algo_name = "gmm"

    items = []
    for uid, info in mapping.items():
        items.append(
            schemas.GlobalClusterItem(
                user_id=uid,
                cluster_id=info["cluster_id"],
                label=info["label"],
            )
        )

    return schemas.GlobalClusterResponse(
        month=req.month,
        algo=algo_name,
        items=items,
    )

# Compatibility endpoint for the frontend: /summaries/{user_id}?month=YYYY-MM
@app.get("/summaries/{user_id}")
def get_monthly_summary_compat(
    user_id: int,
    month: str,
    db: Session = Depends(get_db),
):
    # Reuse the same logic as /analytics/summary
    # If you defined a helper function, call that. Otherwise, copy the body.
    total_income = (
        db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0))
        .join(models.Category, models.Transaction.category_id == models.Category.id)
        .filter(models.Transaction.user_id == user_id)
        .filter(models.Category.type == "income")
        .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
        .scalar()
    )

    total_expense = (
        db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0))
        .join(models.Category, models.Transaction.category_id == models.Category.id)
        .filter(models.Transaction.user_id == user_id)
        .filter(models.Category.type == "expense")
        .filter(func.substr(models.Transaction.transaction_date, 1, 7) == month)
        .scalar()
    )

    net_savings = float(total_income) - float(total_expense)

    return {
        "user_id": user_id,
        "month": month,
        "total_income": float(total_income),
        "total_expense": float(total_expense),
        "net_savings": net_savings,
    }


# -------------------------------------------------------------------
# Analytics API used by the frontend dashboard
# -------------------------------------------------------------------

class AnalyticsSummaryOut(BaseModel):
    user_id: int
    month: str
    total_income: float
    total_expense: float
    net_savings: float


class AnalyticsByCategoryOut(BaseModel):
    category: str
    total_expense: float


class BudgetCompareOut(BaseModel):
    category: str
    month: str
    budget: float
    actual: float
    difference: float  # actual - budget


def _month_filter(column, month: str):
    # transaction_date is stored as 'YYYY-MM-DD'
    # we compare just the 'YYYY-MM' prefix
    return func.substr(column, 1, 7) == month


@app.get("/analytics/summary", response_model=AnalyticsSummaryOut)
def api_analytics_summary(
    user_id: int,
    month: str,
    db: Session = Depends(get_db),
):
    # total income
    total_income = (
        db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0))
        .join(models.Category, models.Transaction.category_id == models.Category.id)
        .filter(models.Transaction.user_id == user_id)
        .filter(models.Category.type == "income")
        .filter(_month_filter(models.Transaction.transaction_date, month))
        .scalar()
    )

    # total expense
    total_expense = (
        db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0))
        .join(models.Category, models.Transaction.category_id == models.Category.id)
        .filter(models.Transaction.user_id == user_id)
        .filter(models.Category.type == "expense")
        .filter(_month_filter(models.Transaction.transaction_date, month))
        .scalar()
    )

    return AnalyticsSummaryOut(
        user_id=user_id,
        month=month,
        total_income=float(total_income),
        total_expense=float(total_expense),
        net_savings=float(total_income) - float(total_expense),
    )


@app.get("/analytics/by_category", response_model=list[AnalyticsByCategoryOut])
def api_analytics_by_category(
    user_id: int,
    month: str,
    db: Session = Depends(get_db),
):
    rows = (
        db.query(
            models.Category.name.label("category"),
            func.coalesce(func.sum(models.Transaction.amount), 0.0).label("total_expense"),
        )
        .join(models.Category, models.Transaction.category_id == models.Category.id)
        .filter(models.Transaction.user_id == user_id)
        .filter(models.Category.type == "expense")
        .filter(_month_filter(models.Transaction.transaction_date, month))
        .group_by(models.Category.id, models.Category.name)
        .order_by(func.sum(models.Transaction.amount).desc())
        .all()
    )

    return [
        AnalyticsByCategoryOut(category=category, total_expense=float(total))
        for category, total in rows
    ]


@app.get("/analytics/budget_compare", response_model=list[BudgetCompareOut])
def api_analytics_budget_compare(
    user_id: int,
    month: str,
    db: Session = Depends(get_db),
):
    """
    For each budgeted category in this month, compare budget vs actual expense.
    """
    rows = (
        db.query(
            models.Category.name.label("category"),
            models.Budget.month,
            models.Budget.amount.label("budget_amount"),
            func.coalesce(func.sum(models.Transaction.amount), 0.0).label("actual_spent"),
        )
        .join(models.Category, models.Budget.category_id == models.Category.id)
        .outerjoin(
            models.Transaction,
            (models.Transaction.user_id == models.Budget.user_id)
            & (models.Transaction.category_id == models.Budget.category_id)
            & _month_filter(models.Transaction.transaction_date, month),
        )
        .filter(models.Budget.user_id == user_id)
        .filter(models.Budget.month == month)
        .group_by(
            models.Category.name,
            models.Budget.month,
            models.Budget.amount,
        )
        .all()
    )

    result: list[BudgetCompareOut] = []
    for category, m, budget_amount, actual_spent in rows:
        actual = float(actual_spent)
        budget = float(budget_amount)
        result.append(
            BudgetCompareOut(
                category=category,
                month=m,
                budget=budget,
                actual=actual,
                difference=actual - budget,
            )
        )
    return result


# from fastapi import FastAPI, Depends, HTTPException
# from sqlalchemy.orm import Session
# from . import models, schemas
# from .db import get_db

# app = FastAPI()

# @app.get("/budgets", response_model=list[schemas.BudgetOut])
# def list_budgets(
#     user_id: int,
#     month: str,
#     db: Session = Depends(get_db),
# ):
#     # Filter by user AND month, and join category to get its name
#     budgets = (
#         db.query(models.Budget)
#         .join(models.Category, models.Budget.category_id == models.Category.id)
#         .filter(
#             models.Budget.user_id == user_id,
#             models.Budget.month == month,
#         )
#         .order_by(models.Category.name)
#         .all()
#     )

#     # Explicitly map category_name for the response
#     result: list[schemas.BudgetOut] = []
#     for b in budgets:
#         result.append(
#             schemas.BudgetOut(
#                 id=b.id,
#                 user_id=b.user_id,
#                 category_id=b.category_id,
#                 category_name=b.category.name,
#                 month=b.month,
#                 amount=b.amount,
#                 created_at=b.created_at,
#             )
#         )
#     return result



# @app.post("/transactions", response_model=schemas.TransactionOut)
# def create_transaction(payload: schemas.TransactionCreate, db: Session = Depends(get_db)):
#     # find category by name for this user
#     category = (
#         db.query(models.Category)
#         .filter(
#             models.Category.user_id == payload.user_id,
#             models.Category.name == payload.category_name,
#         )
#         .first()
#     )
#     if not category:
#         raise HTTPException(status_code=404, detail="Category not found for this user")

#     tx = models.Transaction(
#         user_id=payload.user_id,
#         category_id=category.id,
#         amount=payload.amount,
#         transaction_date=payload.transaction_date,  # already normalized string
#         description=payload.description,
#     )
#     db.add(tx)
#     db.commit()
#     db.refresh(tx)

#     return schemas.TransactionOut(
#         id=tx.id,
#         user_id=tx.user_id,
#         category_id=tx.category_id,
#         category_name=category.name,
#         amount=tx.amount,
#         transaction_date=tx.transaction_date,
#         description=tx.description,
#         created_at=tx.created_at,
#     )

# @app.get("/transactions", response_model=list[schemas.TransactionOut])
# def list_transactions(user_id: int, month: str, db: Session = Depends(get_db)):
#     return (
#         db.query(models.Transaction)
#         .join(models.Category)
#         .filter(
#             models.Transaction.user_id == user_id,
#             models.Transaction.transaction_date.startswith(month),  # 'YYYY-MM'
#         )
#         .order_by(models.Transaction.transaction_date, models.Transaction.id)
#         .all()
#     )

# @app.delete("/transactions/{tx_id}", status_code=204)
# def delete_transaction(tx_id: int, user_id: int, db: Session = Depends(get_db)):
#     tx = (
#         db.query(models.Transaction)
#         .filter(models.Transaction.id == tx_id, models.Transaction.user_id == user_id)
#         .first()
#     )
#     if not tx:
#         raise HTTPException(status_code=404, detail="Transaction not found")
#     db.delete(tx)
#     db.commit()

# @app.post("/budgets", response_model=schemas.BudgetOut)
# def upsert_budget(payload: schemas.BudgetCreate, db: Session = Depends(get_db)):
#     category = (
#         db.query(models.Category)
#         .filter(
#             models.Category.user_id == payload.user_id,
#             models.Category.name == payload.category_name,
#         )
#         .first()
#     )
#     if not category:
#         raise HTTPException(status_code=404, detail="Category not found for this user")

#     budget = (
#         db.query(models.Budget)
#         .filter(
#             models.Budget.user_id == payload.user_id,
#             models.Budget.category_id == category.id,
#             models.Budget.month == payload.month,
#         )
#         .first()
#     )

#     if budget:
#         budget.amount = payload.amount
#     else:
#         budget = models.Budget(
#             user_id=payload.user_id,
#             category_id=category.id,
#             month=payload.month,
#             amount=payload.amount,
#         )
#         db.add(budget)

#     db.commit()
#     db.refresh(budget)

#     return schemas.BudgetOut(
#         id=budget.id,
#         user_id=budget.user_id,
#         category_id=budget.category_id,
#         category_name=category.name,
#         month=budget.month,
#         amount=budget.amount,
#         created_at=budget.created_at,
#     )

# @app.delete("/budgets/{budget_id}", status_code=204)
# def delete_budget(budget_id: int, user_id: int, db: Session = Depends(get_db)):
#     budget = (
#         db.query(models.Budget)
#         .filter(models.Budget.id == budget_id, models.Budget.user_id == user_id)
#         .first()
#     )
#     if not budget:
#         raise HTTPException(status_code=404, detail="Budget not found")
#     db.delete(budget)
#     db.commit()
