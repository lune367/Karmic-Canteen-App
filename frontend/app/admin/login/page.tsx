"use client"

import type React from "react"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export default function AdminLogin() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const router = useRouter()

  const handleLogin = async (e: React.FormEvent) => {
  e.preventDefault()
  try {
    await login(username, password, true) // true = isAdmin
    router.push("/admin/dashboard")
  } catch (error) {
    if (error instanceof Error) {
      alert(error.message)
    } else {
      alert("An unknown error occurred")
    }
  }
}
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4 bg-gradient-to-br from-blue-50 via-white to-blue-50">
      <div className="w-full max-w-md">
        {/* Card */}
        <div className="bg-card border border-border rounded-2xl shadow-lg p-8 space-y-6">
          {/* Header */}
          <div className="space-y-2">
            <h1 className="text-3xl font-bold text-foreground">Administrator Login</h1>
            <p className="text-muted-foreground text-sm">Log in to manage menus, reports, and food planning.</p>
          </div>

          {/* Form */}
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="username" className="text-sm font-medium text-foreground">
                Username
              </label>
              <Input
                id="username"
                type="text"
                placeholder="admin"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full rounded-lg bg-input border-border"
              />
            </div>

            {/* Password Input */}
            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium text-foreground">
                Password
              </label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-lg bg-input border-border"
              />
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="flex justify-end">
              <Link href="#" className="text-sm text-primary hover:text-primary/80 transition-colors">
                Forgot Password?
              </Link>
            </div>

            {/* Login Button */}
            <Button
              type="submit"
              className="w-full bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg py-6 font-semibold transition-all duration-200"
            >
              Login
            </Button>
          </form>

          {/* Footer */}
          <div className="text-center text-sm text-muted-foreground">
            <p>
              Not an admin?{" "}
              <Link href="/employee/login" className="text-primary hover:text-primary/80">
                Employee Portal
              </Link>
            </p>
          </div>
        </div>

        {/* Back Link */}
        <div className="mt-6 text-center">
          <Link href="/" className="text-sm text-primary hover:text-primary/80 transition-colors">
            ← Back to Home
          </Link>
        </div>
      </div>
    </main>
  )
}

function login(username: string, password: string, arg2: boolean) {
  throw new Error("Function not implemented.")
}

