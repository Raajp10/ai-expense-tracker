"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useApp } from "@/components/app-provider"
import { api } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"
import { Loader2, Send, Bot, UserIcon } from "lucide-react"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  // store timestamps as ISO strings to avoid hydration mismatches across server/client
  timestamp: string
}

export default function AssistantPage() {
  const { userId, month } = useApp()
  const { toast } = useToast()

  const [isHydrated, setIsHydrated] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hello! I'm Rcube, your AI finance assistant. I read from your stored transactions, budgets, anomalies, and spending segments to answer your questions. Ask me anything about your spending patterns, budget comparisons, or unusual transactions!",
      timestamp: new Date().toISOString(),
    },
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Ensure time formatting only happens on the client to prevent hydration drift
    setIsHydrated(true)
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setLoading(true)

    try {
      const response = await api.askRAG(userId, userMessage.content)

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.answer,
        timestamp: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to get response from assistant",
        variant: "destructive",
      })

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "I apologize, but I encountered an error processing your request. Please try again.",
        timestamp: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-background via-background to-muted/10">
      <div className="flex-1 flex flex-col p-8 overflow-hidden">
        <div className="mb-8 space-y-2">
          <h1 className="text-5xl font-bold tracking-tight bg-gradient-to-r from-primary via-primary to-chart-2 bg-clip-text text-transparent">
            Rcube AI Assistant
          </h1>
          <p className="text-muted-foreground text-lg">Ask questions about your finances and spending patterns</p>
        </div>

        <Card className="flex-1 flex flex-col overflow-hidden border-2 shadow-lg">
          <CardHeader className="border-b-2 border-border">
            <CardTitle className="text-2xl font-bold">Conversation</CardTitle>
            <CardDescription className="text-base">Chat with your AI finance assistant</CardDescription>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto space-y-6 pt-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-4 ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {message.role === "assistant" && (
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-chart-1 to-chart-2 text-white flex items-center justify-center flex-shrink-0 shadow-md">
                    <Bot className="w-6 h-6" />
                  </div>
                )}
                <div
                  className={`max-w-[70%] rounded-2xl p-5 shadow-sm ${
                    message.role === "user"
                      ? "bg-gradient-to-br from-primary to-primary/90 text-primary-foreground"
                      : "bg-card text-foreground border-2 border-border"
                  }`}
                >
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                  <p className={`text-xs mt-3 ${message.role === "user" ? "opacity-70" : "text-muted-foreground"}`}>
                    {isHydrated
                      ? new Date(message.timestamp).toLocaleTimeString()
                      : ""}
                  </p>
                </div>
                {message.role === "user" && (
                  <div className="w-10 h-10 rounded-xl bg-secondary text-secondary-foreground flex items-center justify-center flex-shrink-0 shadow-md">
                    <UserIcon className="w-6 h-6" />
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex gap-4 justify-start">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-chart-1 to-chart-2 text-white flex items-center justify-center flex-shrink-0 shadow-md">
                  <Bot className="w-6 h-6" />
                </div>
                <div className="max-w-[70%] rounded-2xl p-5 bg-card border-2 border-border shadow-sm">
                  <Loader2 className="w-6 h-6 animate-spin text-primary" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </CardContent>
        </Card>

        <Card className="mt-6 border-2">
          <CardContent className="pt-6">
            <form onSubmit={handleSubmit} className="flex gap-3">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask a question about your finances..."
                disabled={loading}
                className="flex-1 h-12 text-base"
              />
              <Button type="submit" disabled={loading || !input.trim()} size="lg" className="px-8">
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="mt-4 flex flex-wrap gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setInput("What were my top spending categories this month?")}
            disabled={loading}
            className="h-10 px-4"
          >
            Top spending categories
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setInput("Why was my spending unusual on certain days?")}
            disabled={loading}
            className="h-10 px-4"
          >
            Explain anomalies
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setInput("What spending segment am I in?")}
            disabled={loading}
            className="h-10 px-4"
          >
            My spending segment
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setInput("Compare my spending across different months")}
            disabled={loading}
            className="h-10 px-4"
          >
            Compare months
          </Button>
        </div>
      </div>
    </div>
  )
}
