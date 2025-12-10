"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useApp } from "@/components/app-provider"
import { api } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"
import { Loader2, User, TrendingUp } from "lucide-react"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts"

interface Segment {
  user_id: number
  month: string
  cluster_id: number
  label: string
  centroid: number[]
  categories: string[]
  totals: Record<string, number>
  ratios: Record<string, number>
}

const COLORS = [
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
  "hsl(var(--chart-5))",
]

export default function ProfilePage() {
  const { userId, month } = useApp()
  const { toast } = useToast()

  const [segment, setSegment] = useState<Segment | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchSegment = async () => {
      setLoading(true)
      try {
        const data = await api.getSegment(userId, month)
        setSegment(data)
      } catch (error) {
        toast({
          title: "Error",
          description: error instanceof Error ? error.message : "Failed to fetch spending profile",
          variant: "destructive",
        })
      } finally {
        setLoading(false)
      }
    }

    fetchSegment()
  }, [userId, month, toast])

  // Prepare data for pie chart
  const pieData = segment
    ? Object.entries(segment.totals).map(([category, value]) => ({
        name: category,
        value: value,
      }))
    : []

  const barData = segment
    ? Object.entries(segment.totals).map(([category, value]) => ({
        category,
        amount: value,
      }))
    : []

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-background via-background to-muted/10">
      <div className="p-8 space-y-8">
        <div className="space-y-2">
          <h1 className="text-5xl font-bold tracking-tight bg-gradient-to-r from-primary via-primary to-chart-2 bg-clip-text text-transparent">
            Spending Profile
          </h1>
          <p className="text-muted-foreground text-lg">Your spending cluster and behavior analysis for {month}</p>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-96">
            <Loader2 className="w-12 h-12 animate-spin text-primary" />
          </div>
        ) : segment ? (
          <>
            <Card className="border-0 bg-gradient-to-br from-chart-1 via-chart-2 to-primary text-white shadow-2xl">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <CardTitle className="text-lg font-semibold uppercase tracking-wide opacity-90">
                  Your Spending Segment
                </CardTitle>
                <div className="p-2 rounded-lg bg-white/20">
                  <User className="h-7 w-7" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold tracking-tight">{segment.label}</div>
                <p className="text-base opacity-90 mt-3">Cluster ID: {segment.cluster_id}</p>
              </CardContent>
            </Card>

            <div className="grid gap-8 lg:grid-cols-2">
              <Card className="border-2">
                <CardHeader className="space-y-1">
                  <CardTitle className="text-2xl font-bold text-foreground">Spending Distribution</CardTitle>
                  <CardDescription className="text-base">Breakdown by category for {month}</CardDescription>
                </CardHeader>
                <CardContent className="pt-4">
                  {pieData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={340}>
                      <PieChart>
                        <Pie
                          data={pieData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                          outerRadius={100}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {pieData.map((entry, index) => (
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
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="flex items-center justify-center h-[340px] text-muted-foreground">
                      No spending data
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card className="border-2">
                <CardHeader className="space-y-1">
                  <CardTitle className="text-2xl font-bold text-foreground">Category Spending</CardTitle>
                  <CardDescription className="text-base">Visual comparison of spending amounts</CardDescription>
                </CardHeader>
                <CardContent className="pt-4">
                  {barData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={340}>
                      <BarChart data={barData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                        <XAxis
                          dataKey="category"
                          fontSize={12}
                          stroke="hsl(var(--foreground))"
                          tick={{ fill: "hsl(var(--foreground))" }}
                        />
                        <YAxis
                          fontSize={12}
                          stroke="hsl(var(--foreground))"
                          tick={{ fill: "hsl(var(--foreground))" }}
                        />
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
                        <Bar dataKey="amount" fill="hsl(var(--chart-1))" radius={[8, 8, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="flex items-center justify-center h-[340px] text-muted-foreground">
                      No spending data
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            <Card className="border-2">
              <CardHeader className="space-y-1">
                <CardTitle className="text-2xl font-bold text-foreground">Category Details</CardTitle>
                <CardDescription className="text-base">Complete breakdown with ratios</CardDescription>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="overflow-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b-2 border-border">
                        <th className="text-left py-4 px-4 font-semibold text-sm uppercase tracking-wide text-foreground">
                          Category
                        </th>
                        <th className="text-right py-4 px-4 font-semibold text-sm uppercase tracking-wide text-foreground">
                          Amount
                        </th>
                        <th className="text-right py-4 px-4 font-semibold text-sm uppercase tracking-wide text-foreground">
                          Ratio
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(segment.totals).map(([category, total], idx) => (
                        <tr key={category} className="border-b hover:bg-accent/50 transition-colors">
                          <td className="py-4 px-4">
                            <div className="flex items-center gap-3">
                              <div
                                className="w-4 h-4 rounded-full"
                                style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                              />
                              <span className="font-medium text-foreground">{category}</span>
                            </div>
                          </td>
                          <td className="text-right py-4 px-4 font-bold text-base text-foreground">
                            ${total.toFixed(2)}
                          </td>
                          <td className="text-right py-4 px-4 text-muted-foreground font-medium">
                            {((segment.ratios[category] || 0) * 100).toFixed(1)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>

            <Card className="border-2">
              <CardHeader className="space-y-1">
                <CardTitle className="text-2xl font-bold flex items-center gap-4 text-foreground">
                  <div className="p-2 rounded-lg bg-chart-1/10">
                    <TrendingUp className="w-6 h-6 text-chart-1" />
                  </div>
                  Profile Insights
                </CardTitle>
                <CardDescription className="text-base">Based on your spending patterns</CardDescription>
              </CardHeader>
              <CardContent className="pt-4 space-y-4">
                <div className="flex items-start gap-4 p-4 bg-gradient-to-r from-muted/50 to-transparent rounded-xl border-l-4 border-chart-1">
                  <div className="w-2 h-2 rounded-full bg-chart-1 mt-2" />
                  <div className="flex-1">
                    <p className="text-base font-semibold text-foreground">Segment: {segment.label}</p>
                    <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
                      You are classified as a <strong>{segment.label}</strong> based on your spending behavior in{" "}
                      {month}.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4 p-4 bg-gradient-to-r from-muted/50 to-transparent rounded-xl border-l-4 border-chart-2">
                  <div className="w-2 h-2 rounded-full bg-chart-2 mt-2" />
                  <div className="flex-1">
                    <p className="text-base font-semibold text-foreground">Active Categories</p>
                    <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
                      You have spending across <strong>{segment.categories.length} categories</strong>:{" "}
                      {segment.categories.join(", ")}.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4 p-4 bg-gradient-to-r from-muted/50 to-transparent rounded-xl border-l-4 border-chart-3">
                  <div className="w-2 h-2 rounded-full bg-chart-3 mt-2" />
                  <div className="flex-1">
                    <p className="text-base font-semibold text-foreground">Top Category</p>
                    <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
                      Your highest spending category is{" "}
                      <strong>{Object.entries(segment.totals).sort((a, b) => b[1] - a[1])[0]?.[0] || "N/A"}</strong>.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        ) : (
          <Card className="border-2">
            <CardContent className="flex flex-col items-center justify-center h-96 text-muted-foreground space-y-2">
              <p className="text-lg font-medium">No spending profile data available for this month</p>
              <p className="text-sm">Add some transactions to generate your profile</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
