from app import db
from models.employee import Employee, MealSelection
from models.meal import MenuItem
from utils.auth import hash_password, verify_password, generate_token
from datetime import datetime, timedelta, time

class EmployeeService:
    
    @staticmethod
    def register_employee(employee_id, name, email, password, department):
        """Register a new employee"""
        if Employee.query.filter_by(employee_id=employee_id).first():
            return None, "Employee ID already exists"
        
        if Employee.query.filter_by(email=email).first():
            return None, "Email already registered"
        
        employee = Employee(
            employee_id=employee_id,
            name=name,
            email=email,
            password=hash_password(password),
            department=department
        )
        
        db.session.add(employee)
        db.session.commit()
        
        return employee, None
    
    @staticmethod
    def login_employee(employee_id, password):
        """Login employee and return token"""
        employee = Employee.query.filter_by(employee_id=employee_id).first()
        
        if not employee or not verify_password(employee.password, password):
            return None, "Invalid credentials"
        
        token = generate_token(employee.id)
        return {'token': token, 'employee': employee.to_dict()}, None
    
    @staticmethod
    def get_employee_profile(employee_id):
        """Get employee profile"""
        employee = Employee.query.get(employee_id)
        if not employee:
            return None, "Employee not found"
        return employee.to_dict(), None
    
    @staticmethod
    def get_daily_menu(date=None):
        """Get menu for a specific date (tomorrow by default)"""
        if date is None:
            date = (datetime.now() + timedelta(days=1)).date()
        
        menu_items = MenuItem.query.filter_by(
            available_date=date,
            is_active=True
        ).all()
        
        menu = {
            'breakfast': [],
            'lunch': [],
            'dinner': []
        }
        
        for item in menu_items:
            menu[item.meal_type].append(item.to_dict())
        
        return menu, None
    
    @staticmethod
    def confirm_meal(employee_id, date, meal_type, menu_item_id):
        """Confirm meal selection"""
        # Check if it's before 9 PM deadline
        now = datetime.now()
        deadline = time(21, 0)  # 9:00 PM
        
        if now.time() > deadline and date.date() == (now + timedelta(days=1)).date():
            return None, "Deadline passed. Cannot confirm meal after 9:00 PM"
        
        # Check if menu item exists
        menu_item = MenuItem.query.get(menu_item_id)
        if not menu_item:
            return None, "Menu item not found"
        
        # Check if already confirmed
        existing = MealSelection.query.filter_by(
            employee_id=employee_id,
            date=date,
            meal_type=meal_type
        ).first()
        
        if existing:
            # Update existing selection
            existing.menu_item_id = menu_item_id
            existing.status = 'confirmed'
            existing.updated_at = datetime.utcnow()
        else:
            # Create new selection
            selection = MealSelection(
                employee_id=employee_id,
                date=date,
                meal_type=meal_type,
                menu_item_id=menu_item_id,
                status='confirmed'
            )
            db.session.add(selection)
        
        db.session.commit()
        return {'message': 'Meal confirmed successfully'}, None
    
    @staticmethod
    def cancel_meal(employee_id, date, meal_type):
        """Cancel meal selection"""
        # Check if it's before 9 PM deadline
        now = datetime.now()
        deadline = time(21, 0)
        
        if now.time() > deadline and date.date() == (now + timedelta(days=1)).date():
            return None, "Deadline passed. Cannot cancel meal after 9:00 PM"
        
        selection = MealSelection.query.filter_by(
            employee_id=employee_id,
            date=date,
            meal_type=meal_type
        ).first()
        
        if not selection:
            return None, "No meal selection found"
        
        selection.status = 'cancelled'
        selection.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {'message': 'Meal cancelled successfully'}, None
    
    @staticmethod
    def get_my_selections(employee_id, start_date=None, end_date=None):
        """Get employee's meal selections"""
        if start_date is None:
            start_date = datetime.now().date()
        if end_date is None:
            end_date = start_date + timedelta(days=7)
        
        selections = MealSelection.query.filter(
            MealSelection.employee_id == employee_id,
            MealSelection.date >= start_date,
            MealSelection.date <= end_date
        ).all()
        
        return [selection.to_dict() for selection in selections], None