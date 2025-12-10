"use client"

import { useEffect, useState } from "react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Moon, Sun, User } from "lucide-react"

interface TopBarProps {
  userId: number
  month: string
  theme: "light" | "dark"
  onUserIdChange: (userId: number) => void
  onMonthChange: (month: string) => void
  onToggleTheme: () => void
}

export function TopBar({ userId, month, theme, onUserIdChange, onMonthChange, onToggleTheme }: TopBarProps) {
  const [username, setUsername] = useState<string>("")

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await fetch(`http://localhost:8000/users/${userId}`)
        if (res.ok) {
          const data = await res.json()
          setUsername(data.name || "User")
        }
      } catch (error) {
        console.error("Failed to fetch user:", error)
      }
    }
    fetchUser()
  }, [userId])

  return (
    <div className="border-b border-border bg-card sticky top-0 z-10 shadow-sm">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-6">
          {username && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-primary/10 border border-primary/20">
              <User className="h-4 w-4 text-primary" />
              <span className="text-sm font-semibold text-foreground">{username}</span>
            </div>
          )}

          <div className="flex items-center gap-2">
            <Label htmlFor="user-id" className="text-sm font-medium whitespace-nowrap text-foreground">
              User ID:
            </Label>
            <Input
              id="user-id"
              type="number"
              value={userId}
              onChange={(e) => onUserIdChange(Number.parseInt(e.target.value) || 1)}
              className="w-24 h-10"
              min={1}
            />
          </div>
          <div className="flex items-center gap-2">
            <Label htmlFor="month" className="text-sm font-medium whitespace-nowrap text-foreground">
              Month:
            </Label>
            <Input
              id="month"
              type="month"
              value={month}
              onChange={(e) => onMonthChange(e.target.value)}
              className="w-40 h-10"
            />
          </div>
        </div>
        <Button variant="ghost" size="icon" onClick={onToggleTheme} title="Toggle theme">
          {theme === "light" ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
        </Button>
      </div>
    </div>
  )
}
