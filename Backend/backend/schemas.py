from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

# ---------- Users ----------

class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str  # plain for now; we will hash it before saving


class UserOut(UserBase):
    id: int

    model_config = {
        "from_attributes": True
    }


# ---------- Categories ----------

class CategoryBase(BaseModel):
    name: str
    type: str  # 'expense' or 'income'


class CategoryCreate(CategoryBase):
    user_id: int


class CategoryOut(CategoryBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


# ---------- Transactions ----------

class TransactionBase(BaseModel):
    user_id: int
    category_id: int
    amount: float
    transaction_date: str  # 'YYYY-MM-DD'
    description: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionOut(TransactionBase):
    id: int

    class Config:
        orm_mode = True


# ---------- Budgets ----------

class BudgetBase(BaseModel):
    user_id: int
    category_id: int
    month: str  # 'YYYY-MM'
    amount: float


class BudgetCreate(BudgetBase):
    pass


class BudgetOut(BudgetBase):
    id: int

    model_config = {
    "from_attributes": True
    }

class MonthlySummaryOut(BaseModel):
    id: int
    user_id: int
    month: str
    total_spent: float
    total_income: float
    summary_text: Optional[str] = None

    model_config = {"from_attributes": True}


class BuildSummaryRequest(BaseModel):
    user_id: int
    month: str  # 'YYYY-MM'


class QARequest(BaseModel):
    user_id: int
    question: str


class QAResponse(BaseModel):
    answer: str
    debug: Optional[str] = None


class DailyAnomalyPoint(BaseModel):
    date: str
    total_amount: float
    z_score: float
    is_anomaly: bool


class DetectDailyAnomaliesRequest(BaseModel):
    user_id: int
    month: str              # 'YYYY-MM'
    z_threshold: float = 2.0


class DetectDailyAnomaliesResponse(BaseModel):
    user_id: int
    month: str
    mean: float
    std: float
    z_threshold: float
    points: list[DailyAnomalyPoint]


# ---------- Anomaly Detection (Step 7 extended) ----------

class DailyAnomalyPoint(BaseModel):
    date: str
    total_amount: float
    z_score: float
    is_anomaly: bool


class DetectDailyAnomaliesRequest(BaseModel):
    user_id: int
    month: str              # 'YYYY-MM'
    z_threshold: float = 2.0


class DetectDailyAnomaliesResponse(BaseModel):
    user_id: int
    month: str
    mean: float
    std: float
    z_threshold: float
    points: list[DailyAnomalyPoint]


class DetectDailyAnomaliesByCategoryRequest(BaseModel):
    user_id: int
    month: str
    category_name: str
    z_threshold: float = 2.0


# same response type as DetectDailyAnomaliesResponse


class TransactionAnomalyPoint(BaseModel):
    id: int
    date: str
    amount: float
    description: Optional[str] = None
    category_name: str
    z_score: float
    is_anomaly: bool


class DetectTransactionAnomaliesRequest(BaseModel):
    user_id: int
    month: str
    z_threshold: float = 2.0


class DetectTransactionAnomaliesResponse(BaseModel):
    user_id: int
    month: str
    mean: float
    std: float
    z_threshold: float
    points: list[TransactionAnomalyPoint]


class DailyPlotPoint(BaseModel):
    date: str
    total_amount: float


class DailyPlotSeriesResponse(BaseModel):
    user_id: int
    month: str
    mean: float
    std: float
    upper_band: float
    lower_band: float
    points: list[DailyPlotPoint]

class ClusterRequest(BaseModel):
    user_id: int
    month: str


class ClusterResponse(BaseModel):
    user_id: int
    month: str
    cluster_id: int
    label: str
    centroid: list[float]
    categories: list[str]
    totals: dict
    ratios: dict

class GlobalClusterRequest(BaseModel):
    month: str
    algo: str = "kmeans"   # "kmeans" or "gmm"
    n_clusters: int = 4

class GlobalClusterItem(BaseModel):
    user_id: int
    cluster_id: int
    label: str


class GlobalClusterResponse(BaseModel):
    month: str
    algo: str
    items: list[GlobalClusterItem]


# class BudgetOut(BaseModel):
#     id: int
#     user_id: int
#     category_id: int
#     category_name: str
#     month: str       # "YYYY-MM"
#     amount: float
#     created_at: datetime

#     class Config:
#         from_attributes = True

# class TransactionCreate(BaseModel):
#     user_id: int
#     category_name: str  # or category_id
#     amount: float
#     transaction_date: date   # <- Pydantic expects YYYY-MM-DD here
#     description: str





# from datetime import datetime

# class TransactionCreate(BaseModel):
#     user_id: int
#     category_name: str
#     amount: float
#     transaction_date: str  # accept raw string
#     description: str

#     # normalize to "YYYY-MM-DD"
#     @field_validator("transaction_date")
#     @classmethod
#     def normalize_date(cls, v: str) -> str:
#         v = v.strip()
#         # already ISO?
#         try:
#             d = datetime.strptime(v, "%Y-%m-%d")
#             return d.strftime("%Y-%m-%d")
#         except ValueError:
#             pass

#         # dd/mm/yyyy?
#         try:
#             d = datetime.strptime(v, "%d/%m/%Y")
#             return d.strftime("%Y-%m-%d")
#         except ValueError:
#             raise ValueError(
#                 "transaction_date must be in 'YYYY-MM-DD' or 'DD/MM/YYYY' format"
#             )
