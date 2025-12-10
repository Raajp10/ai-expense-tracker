"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useApp } from "@/components/app-provider"
import { api } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"
import { DollarSign, TrendingDown, TrendingUp, Loader2 } from "lucide-react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts"

interface Summary {
  user_id: number
  month: string
  total_income: number
  total_expense: number
  net_savings: number
}

interface CategoryData {
  category: string
  total_expense: number
}

interface BudgetCompare {
  category: string
  month: string
  budget: number
  actual: number
  difference: number
}

const COLORS = [
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
  "hsl(var(--chart-5))",
]

export default function DashboardPage() {
  const { userId, month } = useApp()
  const { toast } = useToast()

  const [summary, setSummary] = useState<Summary | null>(null)
  const [categoryData, setCategoryData] = useState<CategoryData[]>([])
  const [budgetCompare, setBudgetCompare] = useState<BudgetCompare[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const [summaryRes, categoryRes, budgetRes] = await Promise.all([
          api.getSummary(userId, month),
          api.getByCategory(userId, month),
          api.getBudgetCompare(userId, month),
        ])
        setSummary(summaryRes)
        setCategoryData(categoryRes)
        setBudgetCompare(budgetRes)
      } catch (error) {
        toast({
          title: "Error",
          description: error instanceof Error ? error.message : "Failed to fetch dashboard data",
          variant: "destructive",
        })
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [userId, month, toast])

  return (
    <div className="p-8 space-y-8 bg-gradient-to-br from-background via-background to-muted/10">
      <div className="space-y-2">
        <h1 className="text-5xl font-bold tracking-tight bg-gradient-to-r from-primary via-primary to-chart-2 bg-clip-text text-transparent">
          Dashboard
        </h1>
        <p className="text-muted-foreground text-lg">Monthly financial overview for {month}</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-96">
          <Loader2 className="w-12 h-12 animate-spin text-primary" />
        </div>
      ) : (
        <>
          <div className="grid gap-6 md:grid-cols-3">
            <Card className="border-2 hover:shadow-xl transition-all duration-300 hover:scale-[1.02]">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <CardTitle className="text-sm font-bold uppercase tracking-wide text-muted-foreground">
                  Total Income
                </CardTitle>
                <div className="p-3 rounded-xl bg-gradient-to-br from-emerald-500/10 to-emerald-600/10">
                  <TrendingUp className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold tracking-tight text-emerald-600 dark:text-emerald-400">
                  ${summary?.total_income?.toFixed(2) || "0.00"}
                </div>
                <p className="text-sm text-muted-foreground mt-2">For {month}</p>
              </CardContent>
            </Card>

            <Card className="border-2 hover:shadow-xl transition-all duration-300 hover:scale-[1.02]">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <CardTitle className="text-sm font-bold uppercase tracking-wide text-muted-foreground">
                  Total Expense
                </CardTitle>
                <div className="p-3 rounded-xl bg-gradient-to-br from-rose-500/10 to-rose-600/10">
                  <TrendingDown className="h-5 w-5 text-rose-600 dark:text-rose-400" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold tracking-tight text-rose-600 dark:text-rose-400">
                  ${summary?.total_expense?.toFixed(2) || "0.00"}
                </div>
                <p className="text-sm text-muted-foreground mt-2">For {month}</p>
              </CardContent>
            </Card>

            <Card className="border-2 hover:shadow-xl transition-all duration-300 hover:scale-[1.02] bg-gradient-to-br from-primary/5 via-primary/10 to-primary/5">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <CardTitle className="text-sm font-bold uppercase tracking-wide text-primary">Net Savings</CardTitle>
                <div className="p-3 rounded-xl bg-primary/20">
                  <DollarSign className="h-5 w-5 text-primary" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold tracking-tight text-primary">
                  ${summary?.net_savings?.toFixed(2) || "0.00"}
                </div>
                <p className="text-sm text-muted-foreground mt-2">Income - Expense</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-8 lg:grid-cols-2">
            <Card className="border-2 shadow-lg">
              <CardHeader className="space-y-1">
                <CardTitle className="text-3xl font-bold text-foreground">Expense by Category</CardTitle>
                <CardDescription className="text-base">Spending breakdown for {month}</CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
                {categoryData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={350}>
                    <PieChart>
                      <Pie
                        data={categoryData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ category, percent }) => `${category}: ${(percent * 100).toFixed(0)}%`}
                        outerRadius={110}
                        fill="#8884d8"
                        dataKey="total_expense"
                      >
                        {categoryData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip
                        formatter={(value) => `$${Number(value).toFixed(2)}`}
                        contentStyle={{
                          backgroundColor: "hsl(var(--card))",
                          border: "1px solid hsl(var(--border))",
                          borderRadius: "8px",
                          color: "hsl(var(--card-foreground))",
                        }}
                        labelStyle={{ color: "hsl(var(--card-foreground))" }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-[350px] text-muted-foreground">
                    No expense data available
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="border-2 shadow-lg">
              <CardHeader className="space-y-1">
                <CardTitle className="text-3xl font-bold text-foreground">Budget vs Actual</CardTitle>
                <CardDescription className="text-base">How you're tracking against budgets</CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
                {budgetCompare.length > 0 ? (
                  <ResponsiveContainer width="100%" height={350}>
                    <BarChart data={budgetCompare}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis
                        dataKey="category"
                        fontSize={12}
                        stroke="hsl(var(--foreground))"
                        tick={{ fill: "hsl(var(--foreground))" }}
                      />
                      <YAxis fontSize={12} stroke="hsl(var(--foreground))" tick={{ fill: "hsl(var(--foreground))" }} />
                      <Tooltip
                        formatter={(value) => `$${Number(value).toFixed(2)}`}
                        contentStyle={{
                          backgroundColor: "hsl(var(--card))",
                          border: "1px solid hsl(var(--border))",
                          borderRadius: "8px",
                          color: "hsl(var(--card-foreground))",
                        }}
                        labelStyle={{ color: "hsl(var(--card-foreground))" }}
                      />
                      <Bar dataKey="budget" fill="hsl(var(--chart-3))" name="Budget" radius={[8, 8, 0, 0]} />
                      <Bar dataKey="actual" fill="hsl(var(--chart-1))" name="Actual" radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-[350px] text-muted-foreground">
                    No budget data available
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  )
}
