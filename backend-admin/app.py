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
admins_collection = db['admins']
menu_collection = db['menus']
meal_counts_collection = db['meal_counts']

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
            current_admin = admins_collection.find_one({'_id': data['admin_id']}, {'password': 0})
            
            if not current_admin:
                return jsonify({'success': False, 'error': 'Admin not found'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'error': 'Invalid token'}), 401
        
        return f(current_admin, *args, **kwargs)
    
    return decorated

# ============ ADMIN AUTHENTICATION ============
@app.route('/api/admin/register', methods=['POST'])
def admin_register():
    """Register new admin"""
    try:
        data = request.json
        
        # Validation
        required_fields = ['username', 'email', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Check if admin already exists
        if admins_collection.find_one({'$or': [{'username': data['username']}, {'email': data['email']}]}):
            return jsonify({'success': False, 'error': 'Username or email already exists'}), 400
        
        # Create admin
        admin_data = {
            'username': data['username'],
            'email': data['email'],
            'password': generate_password_hash(data['password']),
            'created_at': get_current_time()
        }
        
        result = admins_collection.insert_one(admin_data)
        
        return jsonify({
            'success': True,
            'message': 'Admin registered successfully',
            'admin_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Admin login"""
    try:
        data = request.json
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'success': False, 'error': 'Username and password required'}), 400
        
        admin = admins_collection.find_one({'username': data['username']})
        
        if not admin or not check_password_hash(admin['password'], data['password']):
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Generate JWT token
        token = jwt.encode({
            'admin_id': str(admin['_id']),
            'username': admin['username'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'success': True,
            'token': token,
            'admin': {
                'username': admin['username'],
                'email': admin['email']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/me', methods=['GET'])
@token_required
def get_admin_profile(current_admin):
    """Get current admin profile"""
    return jsonify({
        'success': True,
        'admin': {
            'username': current_admin['username'],
            'email': current_admin['email']
        }
    }), 200

# ============ MENU MANAGEMENT ============
@app.route('/api/admin/menu', methods=['POST'])
@token_required
def create_menu(current_admin):
    """Create or update menu for a specific date and day"""
    try:
        data = request.json
        
        if not data or 'date' not in data or 'day' not in data:
            return jsonify({'success': False, 'error': 'Date and day are required'}), 400
        
        menu_data = {
            'date': data.get('date'),
            'day': data.get('day'),
            'breakfast': data.get('breakfast', []),
            'lunch': data.get('lunch', []),
            'snacks': data.get('snacks', []),
            'updated_at': get_current_time(),
            'updated_by': current_admin['username']
        }
        
        # Upsert menu (update if exists, insert if not)
        menu_collection.update_one(
            {'date': data.get('date')},
            {'$set': menu_data},
            upsert=True
        )
        
        return jsonify({
            'success': True,
            'message': 'Menu created/updated successfully',
            'menu': menu_data
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/menu/<date>', methods=['GET'])
def get_menu(date):
    """Get menu for a specific date (public endpoint for employees)"""
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

@app.route('/api/admin/menu/all', methods=['GET'])
def get_all_menus():
    """Get all menus (public endpoint)"""
    try:
        menus = list(menu_collection.find({}, {'_id': 0}).sort('date', -1))
        
        return jsonify({
            'success': True,
            'count': len(menus),
            'menus': menus
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/menu/<date>', methods=['PUT'])
@token_required
def update_menu(current_admin, date):
    """Update existing menu"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        update_data = {
            'breakfast': data.get('breakfast'),
            'lunch': data.get('lunch'),
            'snacks': data.get('snacks'),
            'day': data.get('day'),
            'updated_at': get_current_time(),
            'updated_by': current_admin['username']
        }
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        result = menu_collection.update_one(
            {'date': date},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'success': False, 'message': 'Menu not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Menu updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/menu/<date>', methods=['DELETE'])
@token_required
def delete_menu(current_admin, date):
    """Delete menu for a specific date"""
    try:
        result = menu_collection.delete_one({'date': date})
        
        if result.deleted_count == 0:
            return jsonify({'success': False, 'message': 'Menu not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Menu deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ MEAL COUNT TRACKING ============
@app.route('/api/admin/meal-counts/<date>', methods=['GET'])
@token_required
def get_meal_counts(current_admin, date):
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
                    'snacks_count': 0
                }
            }), 200
            
        return jsonify({'success': True, 'counts': counts}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/meal-counts/range', methods=['GET'])
@token_required
def get_meal_counts_range(current_admin):
    """Get meal counts for a date range"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = {}
        if start_date and end_date:
            query = {'date': {'$gte': start_date, '$lte': end_date}}
        elif start_date:
            query = {'date': {'$gte': start_date}}
        elif end_date:
            query = {'date': {'$lte': end_date}}
        
        counts = list(meal_counts_collection.find(query, {'_id': 0}).sort('date', -1))
        
        return jsonify({
            'success': True,
            'count': len(counts),
            'counts': counts
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ HEALTH CHECK ============
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Karmic Canteen Admin Backend API',
        'status': 'running',
        'version': '1.0',
        'timestamp': get_current_time()
    }), 200

@app.route('/api/admin/health', methods=['GET'])
def health_check():
    try:
        client.server_info()
        db_status = 'connected'
    except:
        db_status = 'disconnected'
    
    return jsonify({
        'status': 'healthy',
        'service': 'admin-backend',
        'timestamp': get_current_time(),
        'database': db_status
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)