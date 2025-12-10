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
import { Loader2, Plus, ArrowUpCircle, ArrowDownCircle } from "lucide-react"

interface Transaction {
  id: number
  user_id: number
  category_name: string
  amount: number
  transaction_date: string
  description: string
}

export default function TransactionsPage() {
  const { userId, month } = useApp()
  const { toast } = useToast()

  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  // Form state - using category_name as string
  const [categoryName, setCategoryName] = useState("")
  const [amount, setAmount] = useState("")
  const [transactionDate, setTransactionDate] = useState("")
  const [description, setDescription] = useState("")

  const fetchTransactions = async () => {
    setLoading(true)
    try {
      const data = await api.getTransactions(userId, month)
      setTransactions(data)
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to fetch transactions",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTransactions()
  }, [userId, month])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!categoryName.trim() || !amount || !transactionDate || !description.trim()) {
      toast({
        title: "Validation Error",
        description: "Please fill in all fields",
        variant: "destructive",
      })
      return
    }

    setSubmitting(true)

    try {
      await api.createTransaction({
        user_id: userId,
        category_name: categoryName.trim(),
        amount: Number.parseFloat(amount),
        transaction_date: transactionDate,
        description: description.trim(),
      })

      toast({
        title: "Success",
        description: "Transaction added successfully",
      })

      // Reset form
      setCategoryName("")
      setAmount("")
      setTransactionDate("")
      setDescription("")

      // Refresh transactions
      await fetchTransactions()
    } catch (error) {
      console.error("Transaction creation error:", error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to create transaction",
        variant: "destructive",
      })
    } finally {
      setSubmitting(false)
    }
  }

  const isIncome = (amount: number) => amount > 0

  return (
    <div className="p-8 space-y-8 bg-gradient-to-br from-background via-background to-muted/10">
      <div className="space-y-2">
        <h1 className="text-5xl font-bold tracking-tight bg-gradient-to-r from-primary via-primary to-chart-2 bg-clip-text text-transparent">
          Transactions
        </h1>
        <p className="text-muted-foreground text-lg">Manage your transactions for {month}</p>
      </div>

      <Card className="border-2 shadow-lg">
        <CardHeader className="space-y-1">
          <CardTitle className="text-3xl font-bold">Add New Transaction</CardTitle>
          <CardDescription className="text-base">Record a new income or expense transaction</CardDescription>
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
                  placeholder="e.g., Food, Salary, Rent"
                  className="h-11"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="amount" className="text-sm font-semibold">
                  Amount (use negative for expenses)
                </Label>
                <Input
                  id="amount"
                  type="number"
                  step="0.01"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  placeholder="100.00 or -50.00"
                  className="h-11"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="date" className="text-sm font-semibold">
                  Date
                </Label>
                <Input
                  id="date"
                  type="date"
                  value={transactionDate}
                  onChange={(e) => setTransactionDate(e.target.value)}
                  className="h-11"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description" className="text-sm font-semibold">
                  Description
                </Label>
                <Input
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Brief description"
                  className="h-11"
                  required
                />
              </div>
            </div>

            <Button type="submit" disabled={submitting} size="lg" className="px-8">
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Adding...
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4 mr-2" />
                  Add Transaction
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card className="border-2 shadow-lg">
        <CardHeader className="space-y-1">
          <CardTitle className="text-3xl font-bold">Transaction History</CardTitle>
          <CardDescription className="text-base">
            {transactions.length} transaction(s) for {month}
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-4">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="w-12 h-12 animate-spin text-primary" />
            </div>
          ) : transactions.length > 0 ? (
            <div className="overflow-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b-2 border-border">
                    <th className="text-left py-4 px-4 font-semibold text-sm uppercase tracking-wide">Date</th>
                    <th className="text-left py-4 px-4 font-semibold text-sm uppercase tracking-wide">Category</th>
                    <th className="text-left py-4 px-4 font-semibold text-sm uppercase tracking-wide">Description</th>
                    <th className="text-right py-4 px-4 font-semibold text-sm uppercase tracking-wide">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((tx) => {
                    const income = isIncome(tx.amount)
                    return (
                      <tr key={tx.id} className="border-b hover:bg-accent/50 transition-colors">
                        <td className="py-4 px-4 font-medium">{tx.transaction_date}</td>
                        <td className="py-4 px-4">
                          <span
                            className={`px-3 py-1.5 rounded-lg text-sm font-medium ${income ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400" : "bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400"}`}
                          >
                            {tx.category_name}
                          </span>
                        </td>
                        <td className="py-4 px-4 text-muted-foreground">{tx.description}</td>
                        <td className="text-right py-4 px-4">
                          <div className="flex items-center justify-end gap-2">
                            {income ? (
                              <ArrowUpCircle className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                            ) : (
                              <ArrowDownCircle className="w-4 h-4 text-rose-600 dark:text-rose-400" />
                            )}
                            <span
                              className={`font-bold text-base ${income ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"}`}
                            >
                              ${Math.abs(tx.amount).toFixed(2)}
                            </span>
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-64 text-muted-foreground space-y-2">
              <p className="text-lg font-medium">No transactions found for {month}</p>
              <p className="text-sm">Add your first transaction above</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
