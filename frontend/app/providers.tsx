"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect } from "react"

const ADMIN_API_URL = ((globalThis as any).process?.env?.NEXT_PUBLIC_ADMIN_API_URL) || 'http://localhost:5001'
const EMPLOYEE_API_URL = ((globalThis as any).process?.env?.NEXT_PUBLIC_EMPLOYEE_API_URL) || 'http://localhost:5002'

export interface MenuItem {
  id: string
  name: string
  mealType: "Breakfast" | "Lunch" | "Snacks"
  day: string
}

interface AuthUser {
  email?: string
  username?: string
  name?: string
  token: string
  isAdmin: boolean
}

interface CanteenContextType {
  // Auth
  user: AuthUser | null
  login: (email: string, password: string, isAdmin: boolean) => Promise<void>
  register: (data: any, isAdmin: boolean) => Promise<void>
  logout: () => void
  
  // Menu
  menuItems: MenuItem[]
  addMenuItem: (item: Omit<MenuItem, 'id'>) => Promise<void>
  deleteMenuItem: (id: string) => Promise<void>
  loadMenuFromAPI: () => Promise<void>
  
  // Meal Preferences
  mealConfirmations: Record<string, { menuDate: string; preferences: boolean[] }>
  confirmMeals: (employeeId: string, preferences: boolean[], menuDate: string) => Promise<void>
  getMealSummary: (menuDate: string) => Record<string, number>
  hasSubmittedToday: (employeeId: string, menuDate: string) => boolean
  getMenuForDay: (day: string) => MenuItem[]
  getMenuDateForSubmission: () => string
  getMealPreference: (date: string) => Promise<any>
}

const CanteenContext = createContext<CanteenContextType | undefined>(undefined)

export function CanteenProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [menuItems, setMenuItems] = useState<MenuItem[]>([])
  const [mealConfirmations, setMealConfirmations] = useState<Record<string, { menuDate: string; preferences: boolean[] }>>({})
  const [hydrated, setHydrated] = useState(false)

  // Load from localStorage on mount
  useEffect(() => {
    const savedUser = localStorage.getItem("user")
    const savedMenuItems = localStorage.getItem("menuItems")
    const savedConfirmations = localStorage.getItem("mealConfirmations")

    if (savedUser) {
      setUser(JSON.parse(savedUser))
    }
    if (savedMenuItems) {
      setMenuItems(JSON.parse(savedMenuItems))
    }
    if (savedConfirmations) {
      setMealConfirmations(JSON.parse(savedConfirmations))
    }
    setHydrated(true)
  }, [])

  // Save user to localStorage
  useEffect(() => {
    if (hydrated) {
      if (user) {
        localStorage.setItem("user", JSON.stringify(user))
      } else {
        localStorage.removeItem("user")
      }
    }
  }, [user, hydrated])

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

  // Authentication functions
  const login = async (email: string, password: string, isAdmin: boolean) => {
    const apiUrl = isAdmin ? ADMIN_API_URL : EMPLOYEE_API_URL
    const endpoint = isAdmin ? '/api/admin/login' : '/api/employee/login'
    
    const response = await fetch(`${apiUrl}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(isAdmin ? { username: email, password } : { email, password })
    })

    const data = await response.json()
    
    if (!data.success) {
      throw new Error(data.error || 'Login failed')
    }

    setUser({
      ...(data.admin || data.employee),
      token: data.token,
      isAdmin
    })
  }

  const register = async (registerData: any, isAdmin: boolean) => {
    const apiUrl = isAdmin ? ADMIN_API_URL : EMPLOYEE_API_URL
    const endpoint = isAdmin ? '/api/admin/register' : '/api/employee/register'
    
    const response = await fetch(`${apiUrl}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(registerData)
    })

    const data = await response.json()
    
    if (!data.success) {
      throw new Error(data.error || 'Registration failed')
    }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem("user")
  }

  // Menu functions
  const loadMenuFromAPI = async () => {
    if (!user) return
    
    const apiUrl = user.isAdmin ? ADMIN_API_URL : EMPLOYEE_API_URL
    const endpoint = '/api/admin/menu/all'
    
    const response = await fetch(`${apiUrl}${endpoint}`, {
      headers: {
        'Authorization': `Bearer ${user.token}`
      }
    })

    const data = await response.json()
    
    if (data.success && data.menus) {
      // Convert API format to local format
      const items: MenuItem[] = []
      data.menus.forEach((menu: any) => {
        const day = menu.day
        
        menu.breakfast?.forEach((item: string) => {
          items.push({
            id: `${day}-breakfast-${item}`,
            name: item,
            mealType: "Breakfast",
            day
          })
        })
        
        menu.lunch?.forEach((item: string) => {
          items.push({
            id: `${day}-lunch-${item}`,
            name: item,
            mealType: "Lunch",
            day
          })
        })
        
        menu.snacks?.forEach((item: string) => {
          items.push({
            id: `${day}-snacks-${item}`,
            name: item,
            mealType: "Snacks",
            day
          })
        })
      })
      
      setMenuItems(items)
    }
  }

  const addMenuItem = async (item: Omit<MenuItem, 'id'>) => {
    if (!user || !user.isAdmin) {
      throw new Error('Only admins can add menu items')
    }

    const newItem = { ...item, id: Date.now().toString() }
    
    // Group by day and meal type
    const dayMenu = menuItems.filter(i => i.day === item.day)
    const breakfast = dayMenu.filter(i => i.mealType === 'Breakfast').map(i => i.name)
    const lunch = dayMenu.filter(i => i.mealType === 'Lunch').map(i => i.name)
    const snacks = dayMenu.filter(i => i.mealType === 'Snacks').map(i => i.name)
    
    // Add new item
    if (item.mealType === 'Breakfast') breakfast.push(item.name)
    else if (item.mealType === 'Lunch') lunch.push(item.name)
    else snacks.push(item.name)

    // Calculate date (example: use current week)
    const today = new Date()
    const dayIndex = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].indexOf(item.day)
    const currentDayIndex = today.getDay() === 0 ? 6 : today.getDay() - 1
    const daysToAdd = dayIndex - currentDayIndex
    const menuDate = new Date(today)
    menuDate.setDate(today.getDate() + daysToAdd)
    
    const response = await fetch(`${ADMIN_API_URL}/api/admin/menu`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${user.token}`
      },
      body: JSON.stringify({
        date: menuDate.toISOString().split('T')[0],
        day: item.day,
        breakfast,
        lunch,
        snacks
      })
    })

    const data = await response.json()
    
    if (!data.success) {
      throw new Error(data.error || 'Failed to add menu item')
    }

    setMenuItems((prev) => [...prev, newItem])
  }

  const deleteMenuItem = async (id: string) => {
    if (!user || !user.isAdmin) {
      throw new Error('Only admins can delete menu items')
    }

    const item = menuItems.find(i => i.id === id)
    if (!item) return

    // Update menu on server
    const dayMenu = menuItems.filter(i => i.day === item.day && i.id !== id)
    const breakfast = dayMenu.filter(i => i.mealType === 'Breakfast').map(i => i.name)
    const lunch = dayMenu.filter(i => i.mealType === 'Lunch').map(i => i.name)
    const snacks = dayMenu.filter(i => i.mealType === 'Snacks').map(i => i.name)

    const today = new Date()
    const dayIndex = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].indexOf(item.day)
    const currentDayIndex = today.getDay() === 0 ? 6 : today.getDay() - 1
    const daysToAdd = dayIndex - currentDayIndex
    const menuDate = new Date(today)
    menuDate.setDate(today.getDate() + daysToAdd)
    
    await fetch(`${ADMIN_API_URL}/api/admin/menu/${menuDate.toISOString().split('T')[0]}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${user.token}`
      },
      body: JSON.stringify({
        day: item.day,
        breakfast,
        lunch,
        snacks
      })
    })

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

  const confirmMeals = async (employeeId: string, preferences: boolean[], menuDate: string) => {
    if (!user || user.isAdmin) {
      throw new Error('Only employees can confirm meals')
    }

    // Calculate actual date
    const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    const dayIndex = days.indexOf(menuDate)
    const today = new Date()
    const currentDayIndex = today.getDay() === 0 ? 6 : today.getDay() - 1
    const daysToAdd = dayIndex - currentDayIndex + (today.getHours() >= 21 ? 7 : 0)
    const actualDate = new Date(today)
    actualDate.setDate(today.getDate() + daysToAdd)

    const response = await fetch(`${EMPLOYEE_API_URL}/api/employee/meal-preference`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${user.token}`
      },
      body: JSON.stringify({
        date: actualDate.toISOString().split('T')[0],
        breakfast: preferences[0],
        lunch: preferences[1],
        snacks: preferences[2]
      })
    })

    const data = await response.json()
    
    if (!data.success) {
      throw new Error(data.error || 'Failed to confirm meals')
    }

    setMealConfirmations((prev: any) => ({
      ...prev,
      [employeeId]: { menuDate, preferences },
    }))
  }

  const getMealPreference = async (date: string) => {
    if (!user || user.isAdmin) return null

    const response = await fetch(`${EMPLOYEE_API_URL}/api/employee/meal-preference/${date}`, {
      headers: {
        'Authorization': `Bearer ${user.token}`
      }
    })

    const data = await response.json()
    return data.success ? data.preference : null
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
        user,
        login,
        register,
        logout,
        menuItems,
        addMenuItem,
        deleteMenuItem,
        loadMenuFromAPI,
        mealConfirmations,
        confirmMeals,
        getMealSummary,
        hasSubmittedToday,
        getMenuForDay,
        getMenuDateForSubmission,
        getMealPreference,
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