"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect } from "react"

export interface MenuItem {
  id: string
  name: string
  mealType: "Breakfast" | "Lunch" | "Snacks"
  day: string // day of week: Monday, Tuesday, etc.
}

export interface EmployeeMealConfirmation {
  mealType: "Breakfast" | "Lunch" | "Snacks"
  count: number
}

interface CanteenContextType {
  menuItems: MenuItem[]
  addMenuItem: (item: MenuItem) => void
  deleteMenuItem: (id: string) => void
  mealConfirmations: Record<string, { menuDate: string; preferences: boolean[] }>
  confirmMeals: (employeeId: string, preferences: boolean[], menuDate: string) => void
  getMealSummary: (menuDate: string) => Record<string, number>
  hasSubmittedToday: (employeeId: string, menuDate: string) => boolean
  getMenuForDay: (day: string) => MenuItem[]
  getMenuDateForSubmission: () => string // new function to get the menu date to display
}

const CanteenContext = createContext<CanteenContextType | undefined>(undefined)

export function CanteenProvider({ children }: { children: React.ReactNode }) {
  const [menuItems, setMenuItems] = useState<MenuItem[]>([])
  const [mealConfirmations, setMealConfirmations] = useState<
    Record<string, { menuDate: string; preferences: boolean[] }>
  >({})
  const [hydrated, setHydrated] = useState(false)

  // Load from localStorage on mount
  useEffect(() => {
    const savedMenuItems = localStorage.getItem("menuItems")
    const savedConfirmations = localStorage.getItem("mealConfirmations")

    if (savedMenuItems) {
      setMenuItems(JSON.parse(savedMenuItems))
    }
    if (savedConfirmations) {
      setMealConfirmations(JSON.parse(savedConfirmations))
    }
    setHydrated(true)
  }, [])

  // Save menuItems to localStorage
  useEffect(() => {
    if (hydrated) {
      localStorage.setItem("menuItems", JSON.stringify(menuItems))
    }
  }, [menuItems, hydrated])

  // Save confirmations to localStorage
  useEffect(() => {
    if (hydrated) {
      localStorage.setItem("mealConfirmations", JSON.stringify(mealConfirmations))
    }
  }, [mealConfirmations, hydrated])

  const addMenuItem = (item: MenuItem) => {
    setMenuItems((prev) => [...prev, item])
  }

  const deleteMenuItem = (id: string) => {
    setMenuItems((prev) => prev.filter((item) => item.id !== id))
  }

  const getMenuDateForSubmission = () => {
    const now = new Date()
    const hours = now.getHours()
    const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    // Before 9 PM: show tomorrow's menu
    // After 9 PM: show day after tomorrow's menu
    const daysToAdd = hours >= 21 ? 2 : 1
    const menuDate = new Date(now)
    menuDate.setDate(menuDate.getDate() + daysToAdd)

    return days[menuDate.getDay()]
  }

  const confirmMeals = (employeeId: string, preferences: boolean[], menuDate: string) => {
    setMealConfirmations((prev) => ({
      ...prev,
      [employeeId]: { menuDate, preferences },
    }))
  }

  const hasSubmittedToday = (employeeId: string, menuDate: string) => {
    const submission = mealConfirmations[employeeId]
    return submission && submission.menuDate === menuDate
  }

  const getMealSummary = (menuDate: string) => {
    const summary = {
      Breakfast: 0,
      Lunch: 0,
      Snacks: 0,
    }

    Object.values(mealConfirmations).forEach((data) => {
      // Only count submissions for the specified menu date
      if (data.menuDate === menuDate) {
        if (data.preferences[0]) summary["Breakfast"]++
        if (data.preferences[1]) summary["Lunch"]++
        if (data.preferences[2]) summary["Snacks"]++
      }
    })

    return summary
  }

  const getMenuForDay = (day: string) => {
    return menuItems.filter((item) => item.day === day)
  }

  if (!hydrated) return <>{children}</>

  return (
    <CanteenContext.Provider
      value={{
        menuItems,
        addMenuItem,
        deleteMenuItem,
        mealConfirmations,
        confirmMeals,
        getMealSummary,
        hasSubmittedToday,
        getMenuForDay,
        getMenuDateForSubmission,
      }}
    >
      {children}
    </CanteenContext.Provider>
  )
}

export function useCanteen() {
  const context = useContext(CanteenContext)
  if (!context) {
    throw new Error("useCanteen must be used within CanteenProvider")
  }
  return context
}
