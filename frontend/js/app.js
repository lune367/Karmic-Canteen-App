// Utility function to get today's date string
function getTodayString() {
  const today = new Date()
  return today.toISOString().split("T")[0]
}

function getMenuDateForPrep() {
  const now = new Date()
  const hour = now.getHours()
  const minute = now.getMinutes()
  const isAfter9PM = hour >= 21

  const menuDate = new Date(now)
  if (isAfter9PM) {
    menuDate.setDate(menuDate.getDate() + 2) // Day after tomorrow
  } else {
    menuDate.setDate(menuDate.getDate() + 1) // Tomorrow
  }

  return menuDate
}

function getMenuDateString() {
  const menuDate = getMenuDateForPrep()
  const year = menuDate.getFullYear()
  const month = String(menuDate.getMonth() + 1).padStart(2, "0")
  const day = String(menuDate.getDate()).padStart(2, "0")
  return `${year}-${month}-${day}`
}

// Initialize default weekly menu if not exists
function initializeDefaultMenu() {
  if (!localStorage.getItem("weeklyMenu")) {
    const defaultMenu = {
      Monday: {
        Breakfast: ["Oatmeal", "Toast", "Juice"],
        Lunch: ["Chicken Rice", "Salad", "Water"],
        Snacks: ["Cookies", "Fruit", "Tea"],
      },
      Tuesday: {
        Breakfast: ["Eggs", "Bread", "Milk"],
        Lunch: ["Fish Curry", "Rice", "Water"],
        Snacks: ["Biscuits", "Apple", "Coffee"],
      },
      Wednesday: {
        Breakfast: ["Pancakes", "Syrup", "OJ"],
        Lunch: ["Veggie Stir Fry", "Rice", "Water"],
        Snacks: ["Cake", "Banana", "Tea"],
      },
      Thursday: {
        Breakfast: ["Cereal", "Milk", "Toast"],
        Lunch: ["Mutton Biryani", "Raita", "Water"],
        Snacks: ["Donut", "Orange", "Coffee"],
      },
      Friday: {
        Breakfast: ["Yogurt", "Granola", "Juice"],
        Lunch: ["Paneer Butter", "Naan", "Water"],
        Snacks: ["Muffin", "Grapes", "Tea"],
      },
      Saturday: {
        Breakfast: ["French Toast", "Berries", "Milk"],
        Lunch: ["Tandoori Chicken", "Roti", "Water"],
        Snacks: ["Brownie", "Mango", "Coffee"],
      },
      Sunday: {
        Breakfast: ["Waffle", "Honey", "Juice"],
        Lunch: ["Butter Chicken", "Paratha", "Water"],
        Snacks: ["Pie", "Watermelon", "Tea"],
      },
    }
    localStorage.setItem("weeklyMenu", JSON.stringify(defaultMenu))
  }
}

// Initialize on page load
initializeDefaultMenu()
