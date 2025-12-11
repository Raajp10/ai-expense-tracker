import type React from "react"
import type { Metadata } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import { AppProvider } from "@/components/app-provider"
import { Toaster } from "@/components/ui/toaster"
import { ClientLayout } from "@/components/client-layout"
import "./globals.css"

const _geist = Geist({ subsets: ["latin"] })
const _geistMono = Geist_Mono({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "AI Expense Tracker",
  description: "AI-powered expense tracking with assistant, anomalies, and spending insights",
  icons: {
    icon: [
      {
        url: "/icon.svg",
        type: "image/svg+xml",
      },
    ],
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      {/* suppressHydrationWarning on body to ignore client-only attrs injected by extensions (e.g., cz-shortcut-listen) */}
      <body className="font-sans antialiased" suppressHydrationWarning>
        <AppProvider>
          <ClientLayout>{children}</ClientLayout>
          <Toaster />
        </AppProvider>
        <Analytics />
      </body>
    </html>
  )
}
