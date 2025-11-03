"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { useCanteen } from "@/app/providers"
import { useState, useEffect } from "react"
import router from "next/router"

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
const MEAL_TYPES = ["Breakfast", "Lunch", "Snacks"]

export default function AdminDashboard() {
  const context = useCanteen()
  const [menuDate, setMenuDate] = useState("")

  useEffect(() => {
  if (!context.user || !context.user.isAdmin) {
    router.push('/admin/login')
  } else {
    context.loadMenuFromAPI()
  }
}, [context.user])

  const mealSummary = context.getMealSummary(menuDate)
  const totalConfirmations = Object.values(mealSummary).reduce((sum, count) => sum + (count as number), 0)

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Navigation */}
      <nav className="bg-card border-b border-border shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-foreground">Canteen Administration Panel</h1>
          <Link href="/">
            <Button variant="outline" className="rounded-lg bg-transparent">
              Logout
            </Button>
          </Link>
        </div>
      </nav>

      {/* Dashboard Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="space-y-8">
          {/* Add / Edit Menu Section */}
          <div className="bg-card border border-border rounded-2xl shadow-lg p-8">
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">Menu Management</h2>
              <p className="text-muted-foreground">Add, edit, or delete food items for each day</p>
              <Link href="/admin/menu">
                <Button className="bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg py-6 font-semibold transition-all duration-200">
                  Add / Edit Menu
                </Button>
              </Link>
            </div>
          </div>

          {/* Employee Meal Summary Section */}
          <div className="bg-card border border-border rounded-2xl shadow-lg p-8">
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-foreground mb-2">Employee Meal Summary - {menuDate}</h2>
                <p className="text-muted-foreground">Total meal selections for {menuDate}</p>
              </div>

              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Total Confirmations */}
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-6">
                  <p className="text-sm text-muted-foreground mb-1">Total Employees Selected</p>
                  <p className="text-4xl font-bold text-primary">{totalConfirmations}</p>
                </div>

                {/* Breakfast Count */}
                <div className="bg-gradient-to-br from-amber-50 to-amber-100 border border-amber-200 rounded-lg p-6">
                  <p className="text-sm text-muted-foreground mb-1">Breakfast</p>
                  <p className="text-4xl font-bold text-amber-700">{mealSummary["Breakfast"]}</p>
                </div>

                {/* Lunch Count */}
                <div className="bg-gradient-to-br from-green-50 to-green-100 border border-green-200 rounded-lg p-6">
                  <p className="text-sm text-muted-foreground mb-1">Lunch</p>
                  <p className="text-4xl font-bold text-green-700">{mealSummary["Lunch"]}</p>
                </div>

                {/* Snacks Count */}
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-6">
                  <p className="text-sm text-muted-foreground mb-1">Snacks</p>
                  <p className="text-4xl font-bold text-purple-700">{mealSummary["Snacks"]}</p>
                </div>
              </div>

              {/* Meal Type Breakdown */}
              <div className="mt-8">
                <h3 className="text-lg font-semibold text-foreground mb-4">Breakdown by Meal Type</h3>
                <div className="space-y-3">
                  {["Breakfast", "Lunch", "Snacks"].map((type) => (
                    <div
                      key={type}
                      className="flex items-center justify-between bg-muted/30 rounded-lg p-4 border border-border"
                    >
                      <span className="font-medium text-foreground">{type}</span>
                      <span className="text-lg font-bold text-primary">
                        {mealSummary[type as keyof typeof mealSummary]} employees
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="bg-card border border-border rounded-2xl shadow-lg p-8">
            <h2 className="text-2xl font-bold text-foreground mb-6">Weekly Menu (Monday to Sunday)</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-7 gap-4">
              {DAYS.map((day) => {
                const dayMenu = context.getMenuForDay(day)
                return (
                  <div key={day} className="bg-muted/30 rounded-lg p-4 border border-border">
                    <h4 className="font-semibold text-foreground mb-3">{day}</h4>
                    <div className="space-y-2">
                      {MEAL_TYPES.map((mealType) => {
                        const items = dayMenu.filter((item) => item.mealType === mealType)
                        return (
                          <div key={mealType} className="text-sm">
                            <p className="font-medium text-muted-foreground">{mealType}:</p>
                            {items.length > 0 ? (
                              <ul className="list-disc list-inside text-foreground text-xs space-y-1">
                                {items.map((item) => (
                                  <li key={item.id}>{item.name}</li>
                                ))}
                              </ul>
                            ) : (
                              <p className="text-muted-foreground italic text-xs">No items</p>
                            )}
                          </div>
                        )
                      })}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
