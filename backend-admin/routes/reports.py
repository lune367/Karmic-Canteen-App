from fastapi import APIRouter, Depends
from typing import List
from models.report import DailyReport, MealCount, HistoricalData
from database.db import get_db
from routes.auth import get_current_admin

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/daily/{date}", response_model=List[DailyReport])
def get_daily_report(date: str, admin: dict = Depends(get_current_admin)):
    """
    Get consolidated report for a specific date showing meal counts
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all meal types for the date
    cursor.execute(
        """
        SELECT DISTINCT meal_type 
        FROM employee_selections 
        WHERE date = ? AND status = 'confirmed'
        """,
        (date,)
    )
    meal_types = [row[0] for row in cursor.fetchall()]
    
    reports = []
    
    for meal_type in meal_types:
        # Get counts for each menu item
        cursor.execute(
            """
            SELECT m.name, COUNT(e.id) as count
            FROM employee_selections e
            JOIN menu_items m ON e.menu_item_id = m.id
            WHERE e.date = ? AND e.meal_type = ? AND e.status = 'confirmed'
            GROUP BY m.name
            """,
            (date, meal_type)
        )
        
        results = cursor.fetchall()
        meals = [MealCount(menu_item_name=r[0], count=r[1]) for r in results]
        total = sum(m.count for m in meals)
        
        reports.append(
            DailyReport(
                date=date,
                meal_type=meal_type,
                meals=meals,
                total_count=total
            )
        )
    
    conn.close()
    return reports

@router.get("/historical", response_model=List[HistoricalData])
def get_historical_data(start_date: str, end_date: str, admin: dict = Depends(get_current_admin)):
    """
    Get historical data for planning and analysis
    """
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT 
            date,
            meal_type,
            COUNT(*) as count
        FROM employee_selections
        WHERE date BETWEEN ? AND ? AND status = 'confirmed'
        GROUP BY date, meal_type
        ORDER BY date
        """,
        (start_date, end_date)
    )
    
    results = cursor.fetchall()
    conn.close()
    
    # Group by date
    data_by_date = {}
    for row in results:
        date, meal_type, count = row
        if date not in data_by_date:
            data_by_date[date] = {"total": 0, "breakdown": {}}
        data_by_date[date]["total"] += count
        data_by_date[date]["breakdown"][meal_type] = count
    
    return [
        HistoricalData(
            date=date,
            total_meals=data["total"],
            breakdown=data["breakdown"]
        )
        for date, data in data_by_date.items()
    ]

@router.get("/summary/{date}")
def get_date_summary(date: str, admin: dict = Depends(get_current_admin)):
    """
    Get quick summary for a date
    """
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT 
            meal_type,
            COUNT(*) as count
        FROM employee_selections
        WHERE date = ? AND status = 'confirmed'
        GROUP BY meal_type
        """,
        (date,)
    )
    
    results = cursor.fetchall()
    conn.close()
    
    summary = {row[0]: row[1] for row in results}
    total = sum(summary.values())
    
    return {
        "date": date,
        "total_meals": total,
        "breakdown": summary
    }