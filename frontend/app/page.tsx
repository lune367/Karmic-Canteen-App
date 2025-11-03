"use client"
import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4 bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Hero Section */}
      <div className="w-full max-w-2xl text-center space-y-8">
        {/* Header */}
        <div className="space-y-4">
          <h1 className="text-4xl md:text-5xl font-bold text-foreground">Karmic Canteen App</h1>
          <p className="text-lg text-muted-foreground leading-relaxed max-w-xl mx-auto">
            Smart meal management for Karmic Solutions
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center pt-6">
          <Link href="/admin/login" className="flex-1 sm:flex-none">
            <Button className="w-full bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg shadow-md hover:shadow-lg transition-all duration-200 py-6 text-base font-semibold">
              Canteen Administrator
            </Button>
          </Link>

          <Link href="/employee/login" className="flex-1 sm:flex-none">
            <Button className="w-full bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg shadow-md hover:shadow-lg transition-all duration-200 py-6 text-base font-semibold">
              Employee
            </Button>
          </Link>
        </div>
      </div>

      {/* Footer */}
      <div className="absolute bottom-6 text-center text-sm text-muted-foreground">
        <p>Karmic Solutions © 2025</p>
      </div>
    </main>
  )
}
