"use client"

import type React from "react"

import { useApp } from "@/components/app-provider"
import { AppSidebar } from "@/components/app-sidebar"
import { TopBar } from "@/components/top-bar"

export function ClientLayout({ children }: { children: React.ReactNode }) {
  const { userId, month, theme, setUserId, setMonth, toggleTheme } = useApp()

  return (
    <div className="flex min-h-screen">
      <AppSidebar />
      <div className="flex-1 flex flex-col">
        <TopBar
          userId={userId}
          month={month}
          theme={theme}
          onUserIdChange={setUserId}
          onMonthChange={setMonth}
          onToggleTheme={toggleTheme}
        />
        <main className="flex-1 bg-background">{children}</main>
      </div>
    </div>
  )
}
