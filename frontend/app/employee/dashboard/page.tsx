"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { useCanteen } from "@/app/providers"

interface MealPreference {
  id: string
  mealType: "Breakfast" | "Lunch" | "Snacks"
  selected: boolean
}

export default function EmployeeDashboard() {
  const [employeeId, setEmployeeId] = useState("")
  const [menuDate, setMenuDate] = useState("")
  const [mealPreferences, setMealPreferences] = useState<MealPreference[]>([
    { id: "1", mealType: "Breakfast", selected: false },
    { id: "2", mealType: "Lunch", selected: false },
    { id: "3", mealType: "Snacks", selected: false },
  ])
  const [confirmed, setConfirmed] = useState(false)
  const { getMenuForDay, confirmMeals, mealConfirmations, hasSubmittedToday, getMenuDateForSubmission } = useCanteen()

  // Generate a unique employee ID on mount and get current menu date
  useEffect(() => {
    // Get current employee ID
    let id = localStorage.getItem("currentEmployeeId")
    if (!id) {
      id = "EMP_" + Date.now()
      localStorage.setItem("currentEmployeeId", id)
    }
    setEmployeeId(id)

    const date = getMenuDateForSubmission()
    setMenuDate(date)

    // Load previous preferences if exists
    const submission = mealConfirmations[id]
    if (submission && submission.menuDate === date) {
      setMealPreferences((prev) =>
        prev.map((pref, idx) => ({
          ...pref,
          selected: submission.preferences[idx] || false,
        })),
      )
    }
  }, [mealConfirmations, getMenuDateForSubmission])

  const toggleMealPreference = (id: string) => {
    setMealPreferences((prev) => prev.map((pref) => (pref.id === id ? { ...pref, selected: !pref.selected } : pref)))
  }

  const handleConfirmMeals = () => {
    const preferences = mealPreferences.map((pref) => pref.selected)
    confirmMeals(employeeId, preferences, menuDate)
    setConfirmed(true)
    setTimeout(() => setConfirmed(false), 3000)
  }

  const todayMenu = getMenuForDay(menuDate)
  const alreadySubmitted = hasSubmittedToday(employeeId, menuDate)

  const groupedMenu = {
    Breakfast: todayMenu.filter((item) => item.mealType === "Breakfast"),
    Lunch: todayMenu.filter((item) => item.mealType === "Lunch"),
    Snacks: todayMenu.filter((item) => item.mealType === "Snacks"),
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Navigation */}
      <nav className="bg-card border-b border-border shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-foreground">Karmic Canteen</h1>
          <Link href="/">
            <Button variant="outline" className="rounded-lg bg-transparent">
              Logout
            </Button>
          </Link>
        </div>
      </nav>

      {/* Dashboard Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Welcome Section */}
        <div className="bg-card border border-border rounded-2xl shadow-lg p-8 mb-8">
          <h2 className="text-3xl font-bold text-primary mb-2">Welcome, Employee!</h2>
          <p className="text-muted-foreground">
            Select your meal preferences for <span className="font-semibold">{menuDate}</span> before 9 PM cutoff.
          </p>
        </div>

        {/* Today's Menu Section */}
        <div className="bg-card border border-border rounded-2xl shadow-lg p-8 mb-8">
          <h3 className="text-xl font-bold text-foreground mb-6">{menuDate}'s Menu</h3>
          <div className="space-y-4">
            {(["Breakfast", "Lunch", "Snacks"] as const).map((mealType) => (
              <div key={mealType} className="bg-muted/30 rounded-lg p-4 border border-border">
                <p className="font-semibold text-foreground mb-2">{mealType}:</p>
                {groupedMenu[mealType].length > 0 ? (
                  <ul className="list-disc list-inside space-y-1">
                    {groupedMenu[mealType].map((item) => (
                      <li key={item.id} className="text-muted-foreground text-sm">
                        {item.name}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-muted-foreground text-sm italic">No items added yet</p>
                )}
              </div>
            ))}
          </div>
        </div>

        {!alreadySubmitted ? (
          <>
            {/* Meal Preferences Section */}
            <div className="bg-card border border-border rounded-2xl shadow-lg p-8 mb-8">
              <h3 className="text-xl font-bold text-foreground mb-6">Confirm Your Meal Preferences</h3>
              <div className="space-y-3">
                {mealPreferences.map((pref) => (
                  <label
                    key={pref.id}
                    className="flex items-center gap-3 bg-muted/30 rounded-lg p-4 border border-border cursor-pointer hover:bg-muted/50 transition-colors"
                  >
                    <input
                      type="checkbox"
                      checked={pref.selected}
                      onChange={() => toggleMealPreference(pref.id)}
                      className="w-5 h-5 rounded border-border cursor-pointer"
                    />
                    <span className="font-medium text-foreground flex-1">{pref.mealType}</span>
                    <span className="text-sm text-muted-foreground">{pref.selected ? "✓ Yes" : "✗ No"}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Confirmation Message */}
            {confirmed && (
              <div className="bg-green-50 border border-green-200 rounded-2xl shadow-lg p-4 mb-8">
                <p className="text-green-700 font-semibold text-center">✓ Meal preferences confirmed!</p>
              </div>
            )}

            {/* Confirm Button */}
            <Button
              onClick={handleConfirmMeals}
              className="w-full bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg py-6 font-semibold transition-all duration-200 mb-4"
            >
              Confirm Meal Preferences
            </Button>

            {/* Cutoff Info */}
            <div className="bg-blue-50 border border-blue-200 rounded-2xl shadow-lg p-4 text-center">
              <p className="text-blue-900 text-sm font-medium">Please confirm your preferences before 9 PM daily.</p>
            </div>
          </>
        ) : (
          <>
            {/* Already Submitted Message */}
            <div className="bg-green-50 border border-green-200 rounded-2xl shadow-lg p-8 text-center">
              <p className="text-green-700 font-semibold text-lg mb-2">✓ Submission Received</p>
              <p className="text-green-600 text-sm">
                You have already submitted your meal preferences for {menuDate}. Please check back tomorrow.
              </p>
            </div>
          </>
        )}
      </div>
    </main>
  )
}
