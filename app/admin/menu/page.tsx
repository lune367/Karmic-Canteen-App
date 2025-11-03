"use client"

import type React from "react"
import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useCanteen } from "@/app/providers"

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

export default function MenuManagement() {
  const [dishName, setDishName] = useState("")
  const [selectedDay, setSelectedDay] = useState<string>("Monday")
  const [mealType, setMealType] = useState<"Breakfast" | "Lunch" | "Snacks">("Breakfast")
  const { menuItems, addMenuItem, deleteMenuItem } = useCanteen()

  const handleAddItem = (e: React.FormEvent) => {
    e.preventDefault()
    if (dishName.trim()) {
      const newItem = {
        id: Date.now().toString(),
        name: dishName,
        mealType,
        day: selectedDay,
      }
      addMenuItem(newItem)
      setDishName("")
      setMealType("Breakfast")
    }
  }

  const groupedByDay = DAYS.reduce(
    (acc, day) => {
      acc[day] = menuItems.filter((item) => item.day === day)
      return acc
    },
    {} as Record<string, typeof menuItems>,
  )

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Navigation */}
      <nav className="bg-card border-b border-border shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-foreground">Manage Daily Menu</h1>
          <Link href="/admin/dashboard">
            <Button variant="outline" className="rounded-lg bg-transparent">
              Back to Dashboard
            </Button>
          </Link>
        </div>
      </nav>

      {/* Content */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Form Section */}
        <div className="bg-card border border-border rounded-2xl shadow-lg p-8 mb-8">
          <h2 className="text-xl font-bold text-foreground mb-6">Add Menu Item</h2>
          <form onSubmit={handleAddItem} className="space-y-4">
            {/* Dish Name Input */}
            <div className="space-y-2">
              <label htmlFor="dish-name" className="text-sm font-medium text-foreground">
                Dish Name
              </label>
              <Input
                id="dish-name"
                type="text"
                placeholder="e.g., Idli, Rice, Dosa"
                value={dishName}
                onChange={(e) => setDishName(e.target.value)}
                className="w-full rounded-lg bg-input border-border"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="day" className="text-sm font-medium text-foreground">
                Day of Week
              </label>
              <select
                id="day"
                value={selectedDay}
                onChange={(e) => setSelectedDay(e.target.value)}
                className="w-full rounded-lg bg-input border border-border px-3 py-2 text-foreground"
              >
                {DAYS.map((day) => (
                  <option key={day} value={day}>
                    {day}
                  </option>
                ))}
              </select>
            </div>

            {/* Meal Type Dropdown */}
            <div className="space-y-2">
              <label htmlFor="meal-type" className="text-sm font-medium text-foreground">
                Meal Type
              </label>
              <select
                id="meal-type"
                value={mealType}
                onChange={(e) => setMealType(e.target.value as "Breakfast" | "Lunch" | "Snacks")}
                className="w-full rounded-lg bg-input border border-border px-3 py-2 text-foreground"
              >
                <option value="Breakfast">Breakfast</option>
                <option value="Lunch">Lunch</option>
                <option value="Snacks">Snacks</option>
              </select>
            </div>

            {/* Add Item Button */}
            <Button
              type="submit"
              className="w-full bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg py-6 font-semibold transition-all duration-200"
            >
              Add Item
            </Button>
          </form>
        </div>

        {/* Menu List by Day */}
        <div className="space-y-6">
          {DAYS.map((day) => (
            <div key={day} className="bg-card border border-border rounded-2xl shadow-lg p-8">
              <h3 className="text-lg font-bold text-foreground mb-4">{day}</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {["Breakfast", "Lunch", "Snacks"].map((mealType) => {
                  const items = groupedByDay[day].filter((item) => item.mealType === mealType)
                  return (
                    <div key={mealType} className="bg-muted/30 rounded-lg p-4 border border-border">
                      <h4 className="font-semibold text-foreground mb-3">{mealType}</h4>
                      {items.length === 0 ? (
                        <p className="text-muted-foreground text-sm">No items</p>
                      ) : (
                        <ul className="space-y-2">
                          {items.map((item) => (
                            <li
                              key={item.id}
                              className="flex items-center justify-between bg-white rounded p-2 border border-border"
                            >
                              <span className="text-foreground text-sm">{item.name}</span>
                              <button
                                onClick={() => deleteMenuItem(item.id)}
                                className="text-destructive hover:text-destructive/80 transition-colors text-lg"
                                aria-label="Delete item"
                              >
                                ×
                              </button>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Back Button */}
        <div className="mt-8">
          <Link href="/admin/dashboard">
            <Button variant="outline" className="w-full rounded-lg bg-transparent">
              Back to Dashboard
            </Button>
          </Link>
        </div>
      </div>
    </main>
  )
}
