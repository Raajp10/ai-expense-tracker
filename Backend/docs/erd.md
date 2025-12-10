```mermaid
erDiagram
    users ||--o{ categories : has
    users ||--o{ transactions : has
    users ||--o{ budgets : has
    categories ||--o{ transactions : has
    categories ||--o{ budgets : has

    users {
        int id
        string name
        string email
        string password_hash
        datetime created_at
    }

    categories {
        int id
        int user_id
        string name
        string type
        datetime created_at
    }

    transactions {
        int id
        int user_id
        int category_id
        decimal amount
        date transaction_date
        string description
        datetime created_at
    }

    budgets {
        int id
        int user_id
        int category_id
        date month
        decimal amount
        datetime created_at
    }

    monthly_summaries {
        int id
        int user_id
        date month
        decimal total_spent
        decimal total_income
        string summary_text
        datetime created_at
    }
