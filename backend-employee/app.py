from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://localhost:5173'])

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Timezone setup - India Standard Time
IST = pytz.timezone('Asia/Kolkata')

# Database connection
client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
db = client['canteen_system']
employees_collection = db['employees']
meal_preferences_collection = db['meal_preferences']
meal_counts_collection = db['meal_counts']
menu_collection = db['menus']

def get_current_time():
    """Get current time in IST"""
    return datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')

# ============ AUTHENTICATION MIDDLEWARE ============
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'success': False, 'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_employee = employees_collection.find_one({'_id': data['employee_id']}, {'password': 0})
            
            if not current_employee:
                return jsonify({'success': False, 'error': 'Employee not found'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'error': 'Invalid token'}), 401
        
        return f(current_employee, *args, **kwargs)
    
    return decorated

# ============ EMPLOYEE AUTHENTICATION ============
@app.route('/api/employee/register', methods=['POST'])
def employee_register():
    """Register new employee"""
    try:
        data = request.json
        
        # Validation
        required_fields = ['employee_id', 'name', 'email', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Check if employee already exists
        if employees_collection.find_one({'$or': [{'employee_id': data['employee_id']}, {'email': data['email']}]}):
            return jsonify({'success': False, 'error': 'Employee ID or email already exists'}), 400
        
        # Create employee
        employee_data = {
            'employee_id': data['employee_id'],
            'name': data['name'],
            'email': data['email'],
            'password': generate_password_hash(data['password']),
            'department': data.get('department', ''),
            'created_at': get_current_time()
        }
        
        result = employees_collection.insert_one(employee_data)
        
        return jsonify({
            'success': True,
            'message': 'Employee registered successfully',
            '_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/employee/login', methods=['POST'])
def employee_login():
    """Employee login"""
    try:
        data = request.json
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
        
        employee = employees_collection.find_one({'email': data['email']})
        
        if not employee or not check_password_hash(employee['password'], data['password']):
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Generate JWT token
        token = jwt.encode({
            'employee_id': str(employee['_id']),
            'email': employee['email'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'success': True,
            'token': token,
            'employee': {
                'employee_id': employee['employee_id'],
                'name': employee['name'],
                'email': employee['email'],
                'department': employee.get('department', '')
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/employee/me', methods=['GET'])
@token_required
def get_employee_profile(current_employee):
    """Get current employee profile"""
    return jsonify({
        'success': True,
        'employee': {
            'employee_id': current_employee['employee_id'],
            'name': current_employee['name'],
            'email': current_employee['email'],
            'department': current_employee.get('department', '')
        }
    }), 200

# ============ MENU ACCESS ============
@app.route('/api/employee/menu/<date>', methods=['GET'])
@token_required
def get_menu(current_employee, date):
    """Get menu for a specific date"""
    try:
        menu = menu_collection.find_one({'date': date}, {'_id': 0})
        
        if not menu:
            return jsonify({
                'success': False,
                'message': 'Menu not found for this date'
            }), 404
            
        return jsonify({'success': True, 'menu': menu}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/employee/menu/week', methods=['GET'])
@token_required
def get_week_menu(current_employee):
    """Get menu for the current week"""
    try:
        # Get date range for current week
        today = datetime.now(IST).date()
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        
        menus = list(menu_collection.find({
            'date': {
                '$gte': start_date.isoformat(),
                '$lte': end_date.isoformat()
            }
        }, {'_id': 0}).sort('date', 1))
        
        return jsonify({
            'success': True,
            'count': len(menus),
            'menus': menus
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ MEAL PREFERENCES ============
@app.route('/api/employee/meal-preference', methods=['POST'])
@token_required
def save_meal_preference(current_employee):
    """Employee selects which meals they want"""
    try:
        data = request.json
        
        if not data or 'date' not in data:
            return jsonify({'success': False, 'error': 'Date is required'}), 400
        
        # Check deadline (9 PM IST)
        now = datetime.now(IST)
        meal_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        
        # Can only submit for tomorrow or later
        if meal_date <= now.date():
            return jsonify({
                'success': False,
                'error': 'Can only submit preferences for future dates'
            }), 400
        
        # Check if before 9 PM deadline
        if now.hour >= 21 and meal_date == (now.date() + timedelta(days=1)):
            return jsonify({
                'success': False,
                'error': 'Deadline passed. Selections close at 9:00 PM'
            }), 400
        
        preference_data = {
            'employee_id': str(current_employee['_id']),
            'employee_name': current_employee['name'],
            'employee_email': current_employee['email'],
            'date': data.get('date'),
            'breakfast': data.get('breakfast', False),
            'lunch': data.get('lunch', False),
            'snacks': data.get('snacks', False),
            'updated_at': get_current_time()
        }
        
        # Update or insert preference
        meal_preferences_collection.update_one(
            {
                'employee_id': str(current_employee['_id']),
                'date': data.get('date')
            },
            {'$set': preference_data},
            upsert=True
        )
        
        # Update meal counts
        update_meal_counts(data.get('date'))
        
        return jsonify({
            'success': True,
            'message': 'Meal preference saved successfully',
            'preference': preference_data
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/employee/meal-preference/<date>', methods=['GET'])
@token_required
def get_meal_preference(current_employee, date):
    """Get employee's meal preference for a specific date"""
    try:
        preference = meal_preferences_collection.find_one(
            {'employee_id': str(current_employee['_id']), 'date': date},
            {'_id': 0}
        )
        
        if not preference:
            return jsonify({
                'success': True,
                'preference': {
                    'employee_id': str(current_employee['_id']),
                    'date': date,
                    'breakfast': False,
                    'lunch': False,
                    'snacks': False
                }
            }), 200
            
        return jsonify({'success': True, 'preference': preference}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/employee/meal-preferences/my', methods=['GET'])
@token_required
def get_my_preferences(current_employee):
    """Get all preferences for current employee"""
    try:
        preferences = list(meal_preferences_collection.find(
            {'employee_id': str(current_employee['_id'])},
            {'_id': 0}
        ).sort('date', -1).limit(30))
        
        return jsonify({
            'success': True,
            'count': len(preferences),
            'preferences': preferences
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ MEAL COUNT AGGREGATION ============
def update_meal_counts(date):
    """Calculate meal counts and store in database"""
    try:
        # Aggregate counts for the date
        pipeline = [
            {'$match': {'date': date}},
            {'$group': {
                '_id': None,
                'breakfast_count': {'$sum': {'$cond': ['$breakfast', 1, 0]}},
                'lunch_count': {'$sum': {'$cond': ['$lunch', 1, 0]}},
                'snacks_count': {'$sum': {'$cond': ['$snacks', 1, 0]}},
                'total_employees': {'$sum': 1}
            }}
        ]
        
        result = list(meal_preferences_collection.aggregate(pipeline))
        
        if result:
            counts = result[0]
            count_data = {
                'date': date,
                'breakfast_count': counts.get('breakfast_count', 0),
                'lunch_count': counts.get('lunch_count', 0),
                'snacks_count': counts.get('snacks_count', 0),
                'total_employees': counts.get('total_employees', 0),
                'updated_at': get_current_time()
            }
        else:
            count_data = {
                'date': date,
                'breakfast_count': 0,
                'lunch_count': 0,
                'snacks_count': 0,
                'total_employees': 0,
                'updated_at': get_current_time()
            }
        
        # Store/update in database
        meal_counts_collection.update_one(
            {'date': date},
            {'$set': count_data},
            upsert=True
        )
        
        print(f"Meal counts updated for {date}: {count_data}")
            
    except Exception as e:
        print(f"Error updating meal counts: {e}")

@app.route('/api/employee/meal-counts/<date>', methods=['GET'])
def get_local_meal_counts(date):
    """Get meal counts for a specific date"""
    try:
        counts = meal_counts_collection.find_one({'date': date}, {'_id': 0})
        
        if not counts:
            return jsonify({
                'success': True,
                'counts': {
                    'date': date,
                    'breakfast_count': 0,
                    'lunch_count': 0,
                    'snacks_count': 0,
                    'total_employees': 0
                }
            }), 200
            
        return jsonify({'success': True, 'counts': counts}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ HEALTH CHECK ============
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Karmic Canteen Employee Backend API',
        'status': 'running',
        'version': '1.0',
        'timestamp': get_current_time()
    }), 200

@app.route('/api/employee/health', methods=['GET'])
def health_check():
    try:
        client.server_info()
        db_status = 'connected'
    except:
        db_status = 'disconnected'
    
    return jsonify({
        'status': 'healthy',
        'service': 'employee-backend',
        'timestamp': get_current_time(),
        'database': db_status
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True)