"use client"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useCanteen } from "@/app/providers"

export default function EmployeeLogin() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const router = useRouter()
  const { login } = useCanteen()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      await login(email, password, false) // false = isEmployee
      router.push("/employee/dashboard")
    } catch (err: any) {
      console.error("Login error:", err)
      setError(err.message || "Login failed. Please check your credentials.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4 bg-gradient-to-br from-blue-50 via-white to-blue-50">
      <div className="w-full max-w-md">
        {/* Card */}
        <div className="bg-card border border-border rounded-2xl shadow-lg p-8 space-y-6">
          {/* Header */}
          <div className="space-y-2">
            <h1 className="text-3xl font-bold text-foreground">Employee Login</h1>
            <p className="text-muted-foreground text-sm">Enter your credentials to confirm daily meal preferences.</p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium text-foreground">
                Email ID
              </label>
              <Input
                id="email"
                type="email"
                placeholder="employee@karmic.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-lg bg-input border-border"
                required
                disabled={loading}
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
                required
                disabled={loading}
              />
            </div>

            {/* Login Button */}
            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg py-6 font-semibold transition-all duration-200"
            >
              {loading ? "Logging in..." : "Login"}
            </Button>
          </form>

          {/* Footer */}
          <div className="text-center text-sm text-muted-foreground space-y-2">
            <p>
              Don't have an account?{" "}
              <Link href="/employee/register" className="text-primary hover:text-primary/80 font-semibold underline">
                Register here
              </Link>
            </p>
            <p>
              Admin user?{" "}
              <Link href="/admin/login" className="text-primary hover:text-primary/80">
                Admin Portal
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

        {/* Debug Info (Remove in production) */}
        <div className="mt-4 p-4 bg-gray-100 rounded-lg text-xs">
          <p className="font-bold mb-2">Debug Info:</p>
          <p>Employee API: {process.env.NEXT_PUBLIC_EMPLOYEE_API_URL || 'http://localhost:5002'}</p>
          <p>Test credentials: email: john@karmic.com, password: employee123</p>
        </div>
      </div>
    </main>
  )
}