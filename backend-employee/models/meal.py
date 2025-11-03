from app import db
from datetime import datetime

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)  # breakfast, lunch, dinner
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # veg, non-veg, vegan
    available_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    selections = db.relationship('MealSelection', backref='menu_item', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'meal_type': self.meal_type,
            'description': self.description,
            'category': self.category,
            'available_date': self.available_date.isoformat(),
            'is_active': self.is_active
        }