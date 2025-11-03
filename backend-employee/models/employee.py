from app import db
from datetime import datetime

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with meal selections
    meal_selections = db.relationship('MealSelection', backref='employee', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'name': self.name,
            'email': self.email,
            'department': self.department
        }


class MealSelection(db.Model):
    __tablename__ = 'meal_selections'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)  # breakfast, lunch, dinner
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'))
    status = db.Column(db.String(20), default='confirmed')  # confirmed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'date': self.date.isoformat(),
            'meal_type': self.meal_type,
            'menu_item_id': self.menu_item_id,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }