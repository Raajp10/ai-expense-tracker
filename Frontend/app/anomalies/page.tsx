"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useApp } from "@/components/app-provider"
import { api } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"
import { Loader2, AlertCircle } from "lucide-react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts"

interface PlotPoint {
  date: string
  total_amount: number
}

interface PlotData {
  user_id: number
  month: string
  mean: number
  std: number
  upper_band: number
  lower_band: number
  points: PlotPoint[]
}

interface DailyAnomalyPoint {
  date: string
  total_amount: number
  z_score: number
  is_anomaly: boolean
}

interface DailyAnomalies {
  user_id: number
  month: string
  mean: number
  std: number
  z_threshold: number
  points: DailyAnomalyPoint[]
}

interface TransactionAnomaly {
  id: number
  date: string
  amount: number
  description: string
  category_name: string
  z_score: number
  is_anomaly: boolean
}

interface TransactionAnomalies {
  user_id: number
  month: string
  mean: number
  std: number
  z_threshold: number
  points: TransactionAnomaly[]
}

export default function AnomaliesPage() {
  const { userId, month } = useApp()
  const { toast } = useToast()

  const [plotData, setPlotData] = useState<PlotData | null>(null)
  const [dailyAnomalies, setDailyAnomalies] = useState<DailyAnomalies | null>(null)
  const [transactionAnomalies, setTransactionAnomalies] = useState<TransactionAnomalies | null>(null)
  const [loading, setLoading] = useState(true)

  const zThreshold = 2.0

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const [plotRes, dailyRes, txRes] = await Promise.all([
          api.getDailyPlot(userId, month, zThreshold),
          api.getDailyAnomalies(userId, month, zThreshold),
          api.getTransactionAnomalies(userId, month, zThreshold),
        ])
        setPlotData(plotRes)
        setDailyAnomalies(dailyRes)
        setTransactionAnomalies(txRes)
      } catch (error) {
        toast({
          title: "Error",
          description: error instanceof Error ? error.message : "Failed to fetch anomaly data",
          variant: "destructive",
        })
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [userId, month, toast])

  const anomalousTransactions = transactionAnomalies?.points.filter((p) => p.is_anomaly) || []

  return (
    <div className="flex flex-col min-h-screen p-8 space-y-8 bg-gradient-to-br from-background via-background to-muted/10">
      <div className="space-y-2">
        <h1 className="text-5xl font-bold tracking-tight bg-gradient-to-r from-primary via-primary to-chart-2 bg-clip-text text-transparent">
          Anomaly Detection
        </h1>
        <p className="text-muted-foreground text-lg">
          Identify unusual spending patterns for {month} (Z-threshold: {zThreshold})
        </p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-96">
          <Loader2 className="w-12 h-12 animate-spin text-primary" />
        </div>
      ) : (
        <>
          <Card className="border-2">
            <CardHeader className="space-y-1">
              <CardTitle className="text-2xl font-bold">Daily Spending Pattern</CardTitle>
              <CardDescription className="text-base">
                Daily totals vs mean (${plotData?.mean.toFixed(2)}) ± {zThreshold}σ bands
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-4">
              {plotData && plotData.points.length > 0 ? (
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={plotData.points}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis dataKey="date" fontSize={12} />
                    <YAxis fontSize={12} />
                    <Tooltip
                      formatter={(value) => `$${Number(value).toFixed(2)}`}
                      contentStyle={{
                        backgroundColor: "hsl(var(--card))",
                        border: "1px solid hsl(var(--border))",
                        borderRadius: "8px",
                      }}
                    />
                    <ReferenceLine
                      y={plotData.mean}
                      stroke="hsl(var(--chart-3))"
                      strokeDasharray="5 5"
                      strokeWidth={2}
                      label={{ value: "Mean", fill: "hsl(var(--chart-3))" }}
                    />
                    <ReferenceLine
                      y={plotData.upper_band}
                      stroke="hsl(var(--destructive))"
                      strokeDasharray="3 3"
                      strokeWidth={2}
                      label={{ value: "Upper", fill: "hsl(var(--destructive))" }}
                    />
                    <ReferenceLine
                      y={plotData.lower_band}
                      stroke="hsl(var(--destructive))"
                      strokeDasharray="3 3"
                      strokeWidth={2}
                      label={{ value: "Lower", fill: "hsl(var(--destructive))" }}
                    />
                    <Line type="monotone" dataKey="total_amount" stroke="hsl(var(--chart-1))" strokeWidth={3} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-[400px] text-muted-foreground">
                  No data available for this month
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="border-2">
            <CardHeader className="space-y-1">
              <CardTitle className="text-2xl font-bold">Daily Anomalies</CardTitle>
              <CardDescription className="text-base">Days with unusual total spending</CardDescription>
            </CardHeader>
            <CardContent className="pt-4">
              {dailyAnomalies && dailyAnomalies.points.length > 0 ? (
                <div className="overflow-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b-2 border-border">
                        <th className="text-left py-4 px-4 font-semibold text-sm uppercase tracking-wide">Date</th>
                        <th className="text-right py-4 px-4 font-semibold text-sm uppercase tracking-wide">
                          Total Amount
                        </th>
                        <th className="text-right py-4 px-4 font-semibold text-sm uppercase tracking-wide">Z-Score</th>
                        <th className="text-center py-4 px-4 font-semibold text-sm uppercase tracking-wide">Anomaly</th>
                      </tr>
                    </thead>
                    <tbody>
                      {dailyAnomalies.points.map((point) => (
                        <tr
                          key={point.date}
                          className={`border-b transition-colors ${point.is_anomaly ? "bg-destructive/10 hover:bg-destructive/20" : "hover:bg-accent/50"}`}
                        >
                          <td className="py-4 px-4 font-medium">{point.date}</td>
                          <td className="text-right py-4 px-4 font-bold text-base">${point.total_amount.toFixed(2)}</td>
                          <td className="text-right py-4 px-4 font-semibold">{point.z_score.toFixed(2)}</td>
                          <td className="text-center py-4 px-4">
                            {point.is_anomaly && (
                              <span className="inline-flex items-center gap-2 text-destructive font-semibold">
                                <AlertCircle className="w-5 h-5" />
                                Yes
                              </span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="flex items-center justify-center h-64 text-muted-foreground">No data available</div>
              )}
            </CardContent>
          </Card>

          <Card className="border-2 border-destructive/20">
            <CardHeader className="space-y-1">
              <CardTitle className="text-2xl font-bold flex items-center gap-2">
                <AlertCircle className="w-6 h-6 text-destructive" />
                Suspicious Transactions
              </CardTitle>
              <CardDescription className="text-base">Individual transactions flagged as anomalies</CardDescription>
            </CardHeader>
            <CardContent className="pt-4">
              {anomalousTransactions.length > 0 ? (
                <div className="overflow-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b-2 border-border">
                        <th className="text-left py-4 px-4 font-semibold text-sm uppercase tracking-wide">Date</th>
                        <th className="text-left py-4 px-4 font-semibold text-sm uppercase tracking-wide">Category</th>
                        <th className="text-left py-4 px-4 font-semibold text-sm uppercase tracking-wide">
                          Description
                        </th>
                        <th className="text-right py-4 px-4 font-semibold text-sm uppercase tracking-wide">Amount</th>
                        <th className="text-right py-4 px-4 font-semibold text-sm uppercase tracking-wide">Z-Score</th>
                      </tr>
                    </thead>
                    <tbody>
                      {anomalousTransactions.map((tx) => (
                        <tr key={tx.id} className="border-b bg-destructive/5 hover:bg-destructive/10 transition-colors">
                          <td className="py-4 px-4 font-medium">{tx.date}</td>
                          <td className="py-4 px-4">
                            <span className="px-3 py-1.5 rounded-lg bg-secondary text-secondary-foreground text-sm font-medium">
                              {tx.category_name}
                            </span>
                          </td>
                          <td className="py-4 px-4 text-muted-foreground">{tx.description}</td>
                          <td className="text-right py-4 px-4 font-bold text-destructive text-base">
                            ${tx.amount.toFixed(2)}
                          </td>
                          <td className="text-right py-4 px-4 font-bold text-base">{tx.z_score.toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-64 text-muted-foreground space-y-2">
                  <p className="text-lg font-medium">No suspicious transactions detected</p>
                  <p className="text-sm">All transactions appear normal</p>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
