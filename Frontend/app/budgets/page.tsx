"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useApp } from "@/components/app-provider"
import { api } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"
import { Loader2, Plus, Target } from "lucide-react"

interface Budget {
  id: number
  user_id: number
  category_name: string
  month: string
  amount: number
}

export default function BudgetsPage() {
  const { userId, month } = useApp()
  const { toast } = useToast()

  const [budgets, setBudgets] = useState<Budget[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  // Form state - using category_name as string
  const [categoryName, setCategoryName] = useState("")
  const [amount, setAmount] = useState("")

  const fetchBudgets = async () => {
    setLoading(true)
    try {
      const data = await api.getBudgets(userId, month)
      setBudgets(data)
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to fetch budgets",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchBudgets()
  }, [userId, month])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!categoryName.trim() || !amount) {
      toast({
        title: "Validation Error",
        description: "Please fill in all fields",
        variant: "destructive",
      })
      return
    }

    setSubmitting(true)

    try {
      await api.createBudget({
        user_id: userId,
        category_name: categoryName.trim(),
        month,
        amount: Number.parseFloat(amount),
      })

      toast({
        title: "Success",
        description: "Budget added/updated successfully",
      })

      // Reset form
      setCategoryName("")
      setAmount("")

      // Refresh budgets
      await fetchBudgets()
    } catch (error) {
      console.error("Budget creation error:", error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to create budget",
        variant: "destructive",
      })
    } finally {
      setSubmitting(false)
    }
  }

  const totalBudget = budgets.reduce((sum, b) => sum + b.amount, 0)

  return (
    <div className="p-8 space-y-8 bg-gradient-to-br from-background via-background to-muted/10">
      <div className="space-y-2">
        <h1 className="text-5xl font-bold tracking-tight bg-gradient-to-r from-primary via-primary to-chart-2 bg-clip-text text-transparent">
          Budgets
        </h1>
        <p className="text-muted-foreground text-lg">Set and manage your category budgets for {month}</p>
      </div>

      <Card className="border-2 bg-gradient-to-br from-primary/90 via-primary to-chart-1 text-primary-foreground shadow-xl">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
          <CardTitle className="text-lg font-bold uppercase tracking-wide">Total Budget</CardTitle>
          <div className="p-3 rounded-xl bg-white/20 backdrop-blur-sm">
            <Target className="h-6 w-6" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-5xl font-bold tracking-tight">${totalBudget.toFixed(2)}</div>
          <p className="text-sm opacity-90 mt-2">Total allocated for {month}</p>
        </CardContent>
      </Card>

      <Card className="border-2 shadow-lg">
        <CardHeader className="space-y-1">
          <CardTitle className="text-3xl font-bold">Add or Update Budget</CardTitle>
          <CardDescription className="text-base">Set a budget limit for a category</CardDescription>
        </CardHeader>
        <CardContent className="pt-2">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="category" className="text-sm font-semibold">
                  Category Name
                </Label>
                <Input
                  id="category"
                  value={categoryName}
                  onChange={(e) => setCategoryName(e.target.value)}
                  placeholder="e.g., Food, Transportation"
                  className="h-11"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="amount" className="text-sm font-semibold">
                  Budget Amount
                </Label>
                <Input
                  id="amount"
                  type="number"
                  step="0.01"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  placeholder="500.00"
                  className="h-11"
                  required
                />
              </div>
            </div>

            <Button type="submit" disabled={submitting} size="lg" className="px-8">
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4 mr-2" />
                  Add/Update Budget
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card className="border-2 shadow-lg">
        <CardHeader className="space-y-1">
          <CardTitle className="text-3xl font-bold">Current Budgets</CardTitle>
          <CardDescription className="text-base">
            {budgets.length} budget(s) for {month}
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-4">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="w-12 h-12 animate-spin text-primary" />
            </div>
          ) : budgets.length > 0 ? (
            <div className="overflow-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b-2 border-border">
                    <th className="text-left py-4 px-4 font-semibold text-sm uppercase tracking-wide">Category</th>
                    <th className="text-left py-4 px-4 font-semibold text-sm uppercase tracking-wide">Month</th>
                    <th className="text-right py-4 px-4 font-semibold text-sm uppercase tracking-wide">
                      Budget Amount
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {budgets.map((budget) => (
                    <tr key={budget.id} className="border-b hover:bg-accent/50 transition-colors">
                      <td className="py-4 px-4">
                        <span className="px-3 py-1.5 rounded-lg bg-secondary text-secondary-foreground text-sm font-medium">
                          {budget.category_name}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-muted-foreground font-medium">{budget.month}</td>
                      <td className="text-right py-4 px-4 font-bold text-lg text-primary">
                        ${budget.amount.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-64 text-muted-foreground space-y-2">
              <p className="text-lg font-medium">No budgets set for {month}</p>
              <p className="text-sm">Add your first budget above</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
