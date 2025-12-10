from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict
from datetime import datetime
from sqlalchemy.orm import Session

from db import SessionLocal
import models



DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def load_categories(db: Session, csv_path: Path, user_id: int) -> None:
    """
    Load base categories for a specific user (user-scoped categories).
    """
    print(f"[categories] Loading from {csv_path} for user_id={user_id}")
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"].strip()
            ctype = row["type"].strip()

            existing = (
                db.query(models.Category)
                .filter(
                    models.Category.user_id == user_id,
                    models.Category.name == name,
                )
                .first()
            )
            if existing:
                print(f"  - Category already exists for user {user_id}: {name}")
                continue

            cat = models.Category(
                user_id=user_id,
                name=name,
                type=ctype,
                created_at=datetime.utcnow(),  # 👈 set created_at
            )
            db.add(cat)
            print(f"  + Created category for user {user_id}: {name} ({ctype})")
        db.commit()


def _get_or_create_category(
    db: Session, user_id: int, name: str, ctype: str = "expense"
) -> models.Category:
    """
    Get or create a category **for a specific user**.
    """
    cat = (
        db.query(models.Category)
        .filter(
            models.Category.user_id == user_id,
            models.Category.name == name,
        )
        .first()
    )
    if cat:
        return cat

    cat = models.Category(
        user_id=user_id,
        name=name,
        type=ctype,
        created_at=datetime.utcnow(),  # 👈 set created_at
    )

    db.add(cat)
    db.commit()
    db.refresh(cat)
    print(f"  + Auto-created category for user {user_id}: {name} ({ctype})")
    return cat


def load_transactions(db: Session, csv_path: Path) -> None:
    print(f"[transactions] Loading from {csv_path}")
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            user_id = int(row["user_id"])
            category_name = row["category_name"].strip()
            amount = float(row["amount"])
            transaction_date = row["transaction_date"].strip()
            description = row.get("description", "").strip()

            # ensure user exists
            user = db.query(models.User).filter(models.User.id == user_id).first()
            if not user:
                print(f"  ! Skipping row: user_id {user_id} not found")
                continue

            # ensure category exists for THIS user
            cat = _get_or_create_category(db, user_id, category_name, "expense")

            tx = models.Transaction(
                user_id=user_id,
                category_id=cat.id,
                amount=amount,
                transaction_date=transaction_date,
                description=description,
                created_at=datetime.utcnow(),  # 👈 set created_at
            )
            db.add(tx)

            print(
                f"  + Tx: user={user_id}, cat={category_name}, "
                f"amount={amount}, date={transaction_date}, desc={description}"
            )
        db.commit()


def load_budgets(db: Session, csv_path: Path) -> None:
    print(f"[budgets] Loading from {csv_path}")
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            user_id = int(row["user_id"])
            category_name = row["category_name"].strip()
            month = row["month"].strip()       # 'YYYY-MM'
            amount = float(row["amount"])

            user = db.query(models.User).filter(models.User.id == user_id).first()
            if not user:
                print(f"  ! Skipping budget: user_id {user_id} not found")
                continue

            cat = _get_or_create_category(db, user_id, category_name, "expense")

            existing = (
                db.query(models.Budget)
                .filter(
                    models.Budget.user_id == user_id,
                    models.Budget.category_id == cat.id,
                    models.Budget.month == month,
                )
                .first()
            )
            if existing:
                print(
                    f"  - Updating budget for user={user_id}, "
                    f"cat={category_name}, month={month}"
                )
                existing.amount = amount
            else:
                b = models.Budget(
                    user_id=user_id,
                    category_id=cat.id,
                    month=month,
                    amount=amount,
                    created_at=datetime.utcnow(),  # 👈 set created_at if your model has this field
                )
                db.add(b)
                print(
                    f"  + Created budget: user={user_id}, cat={category_name}, "
                    f"month={month}, amount={amount}"
                )
        db.commit()


def main():
    print("=== CSV Demo Data Loader ===")
    print(f"DATA_DIR = {DATA_DIR}")

    db: Session = SessionLocal()

    # We need at least one user to attach base categories to.
    default_user = db.query(models.User).first()
    if not default_user:
        print(
            "ERROR: No users found in the database.\n"
            "Please register at least one user via the API (e.g., /auth/register) "
            "before running this loader."
        )
        db.close()
        return

    default_user_id = default_user.id
    print(f"Using default_user_id={default_user_id} for categories.csv")

    cat_csv = DATA_DIR / "categories.csv"
    tx_csv = DATA_DIR / "transactions.csv"
    bud_csv = DATA_DIR / "budgets.csv"

    if cat_csv.exists():
        load_categories(db, cat_csv, default_user_id)
    else:
        print("[categories] categories.csv not found, skipping.")

    if tx_csv.exists():
        load_transactions(db, tx_csv)
    else:
        print("[transactions] transactions.csv not found, skipping.")

    if bud_csv.exists():
        load_budgets(db, bud_csv)
    else:
        print("[budgets] budgets.csv not found, skipping.")

    db.close()
    print("=== Done loading CSV demo data ===")


if __name__ == "__main__":
    main()
