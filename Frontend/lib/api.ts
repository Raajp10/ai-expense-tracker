const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"

export const api = {
  // ============ ANALYTICS (Dashboard) ============

  async getSummary(userId: number, month: string) {
    const res = await fetch(`${API_BASE_URL}/analytics/summary?user_id=${userId}&month=${month}`)
    if (!res.ok) throw new Error("Failed to fetch summary")
    return res.json()
  },

  async getByCategory(userId: number, month: string) {
    const res = await fetch(`${API_BASE_URL}/analytics/by_category?user_id=${userId}&month=${month}`)
    if (!res.ok) throw new Error("Failed to fetch category data")
    return res.json()
  },

  async getBudgetCompare(userId: number, month: string) {
    const res = await fetch(`${API_BASE_URL}/analytics/budget_compare?user_id=${userId}&month=${month}`)
    if (!res.ok) throw new Error("Failed to fetch budget comparison")
    return res.json()
  },

  // ============ TRANSACTIONS ============

  async getTransactions(userId: number, month: string) {
    const res = await fetch(`${API_BASE_URL}/transactions?user_id=${userId}&month=${month}`)
    if (!res.ok) throw new Error("Failed to fetch transactions")
    return res.json()
  },

  async createTransaction(data: {
    user_id: number
    category_name: string
    amount: number
    transaction_date: string
    description: string
  }) {
    const res = await fetch(`${API_BASE_URL}/transactions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: "Failed to create transaction" }))
      // Handle FastAPI error format: detail can be a string or an array of error objects
      let errorMessage = "Failed to create transaction"
      if (error.detail) {
        if (typeof error.detail === "string") {
          errorMessage = error.detail
        } else if (Array.isArray(error.detail)) {
          // FastAPI validation errors are arrays
          errorMessage = error.detail.map((err: any) => `${err.loc?.join(".")}: ${err.msg || err.type}`).join(", ")
        } else {
          // If detail is an object, stringify it properly
          errorMessage = JSON.stringify(error.detail)
        }
      }
      throw new Error(errorMessage)
    }
    return res.json()
  },

  // ============ BUDGETS ============

  async getBudgets(userId: number, month: string) {
    const res = await fetch(`${API_BASE_URL}/budgets?user_id=${userId}&month=${month}`)
    if (!res.ok) throw new Error("Failed to fetch budgets")
    return res.json()
  },

  async createBudget(data: {
    user_id: number
    category_name: string
    month: string
    amount: number
  }) {
    const res = await fetch(`${API_BASE_URL}/budgets`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: "Failed to create budget" }))
      // Handle FastAPI error format: detail can be a string or an array of error objects
      let errorMessage = "Failed to create budget"
      if (error.detail) {
        if (typeof error.detail === "string") {
          errorMessage = error.detail
        } else if (Array.isArray(error.detail)) {
          // FastAPI validation errors are arrays
          errorMessage = error.detail.map((err: any) => `${err.loc?.join(".")}: ${err.msg || err.type}`).join(", ")
        } else {
          // If detail is an object, stringify it properly
          errorMessage = JSON.stringify(error.detail)
        }
      }
      throw new Error(errorMessage)
    }
    return res.json()
  },

  // ============ ANOMALIES ============

  async getDailyAnomalies(userId: number, month: string, zThreshold = 2.0) {
    const res = await fetch(`${API_BASE_URL}/anomalies/daily`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, month, z_threshold: zThreshold }),
    })
    if (!res.ok) throw new Error("Failed to fetch daily anomalies")
    return res.json()
  },

  async getDailyPlot(userId: number, month: string, zThreshold = 2.0) {
    const res = await fetch(`${API_BASE_URL}/anomalies/daily/plot`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, month, z_threshold: zThreshold }),
    })
    if (!res.ok) throw new Error("Failed to fetch daily plot")
    return res.json()
  },

  async getTransactionAnomalies(userId: number, month: string, zThreshold = 2.0) {
    const res = await fetch(`${API_BASE_URL}/anomalies/transactions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, month, z_threshold: zThreshold }),
    })
    if (!res.ok) throw new Error("Failed to fetch transaction anomalies")
    return res.json()
  },

  // ============ CLUSTERING / SPENDING PROFILE ============

  async getSegment(userId: number, month: string) {
    const res = await fetch(`${API_BASE_URL}/cluster/segments`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, month }),
    })
    if (!res.ok) throw new Error("Failed to fetch segment")
    return res.json()
  },

  // ============ RAG AI ASSISTANT ============

  async askRAG(userId: number, question: string) {
    const res = await fetch(`${API_BASE_URL}/rag/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, question }),
    })
    if (!res.ok) throw new Error("Failed to ask RAG")
    return res.json()
  },

  // ============ USER ============

  async getUser(userId: number) {
    const res = await fetch(`${API_BASE_URL}/users/${userId}`)
    if (!res.ok) throw new Error("Failed to fetch user")
    return res.json()
  },
}
