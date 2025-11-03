from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.menu import MenuItemCreate, MenuItemUpdate, MenuItemResponse
from database.db import get_db
from routes.auth import get_current_admin

router = APIRouter(prefix="/menu", tags=["Menu Management"])

@router.post("/", response_model=MenuItemResponse)
def create_menu_item(item: MenuItemCreate, admin: dict = Depends(get_current_admin)):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO menu_items (name, category, meal_type, date) VALUES (?, ?, ?, ?)",
        (item.name, item.category, item.meal_type, item.date)
    )
    conn.commit()
    
    item_id = cursor.lastrowid
    cursor.execute("SELECT * FROM menu_items WHERE id = ?", (item_id,))
    result = cursor.fetchone()
    conn.close()
    
    return MenuItemResponse(
        id=result[0],
        name=result[1],
        category=result[2],
        meal_type=result[3],
        date=result[4],
        is_available=bool(result[5])
    )

@router.get("/", response_model=List[MenuItemResponse])
def get_menu_items(date: str = None, meal_type: str = None):
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM menu_items WHERE 1=1"
    params = []
    
    if date:
        query += " AND date = ?"
        params.append(date)
    
    if meal_type:
        query += " AND meal_type = ?"
        params.append(meal_type)
    
    query += " ORDER BY date DESC, meal_type"
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    
    return [
        MenuItemResponse(
            id=r[0],
            name=r[1],
            category=r[2],
            meal_type=r[3],
            date=r[4],
            is_available=bool(r[5])
        ) for r in results
    ]

@router.put("/{item_id}", response_model=MenuItemResponse)
def update_menu_item(item_id: int, item: MenuItemUpdate, admin: dict = Depends(get_current_admin)):
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if item exists
    cursor.execute("SELECT * FROM menu_items WHERE id = ?", (item_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # Build update query
    updates = []
    params = []
    
    if item.name:
        updates.append("name = ?")
        params.append(item.name)
    if item.category:
        updates.append("category = ?")
        params.append(item.category)
    if item.meal_type:
        updates.append("meal_type = ?")
        params.append(item.meal_type)
    if item.date:
        updates.append("date = ?")
        params.append(item.date)
    if item.is_available is not None:
        updates.append("is_available = ?")
        params.append(int(item.is_available))
    
    if updates:
        params.append(item_id)
        query = f"UPDATE menu_items SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
    
    cursor.execute("SELECT * FROM menu_items WHERE id = ?", (item_id,))
    result = cursor.fetchone()
    conn.close()
    
    return MenuItemResponse(
        id=result[0],
        name=result[1],
        category=result[2],
        meal_type=result[3],
        date=result[4],
        is_available=bool(result[5])
    )

@router.delete("/{item_id}")
def delete_menu_item(item_id: int, admin: dict = Depends(get_current_admin)):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    conn.commit()
    conn.close()
    
    return {"message": "Menu item deleted successfully"}