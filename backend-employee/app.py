from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import requests
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Timezone setup - India Standard Time
IST = pytz.timezone('Asia/Kolkata')

# Database connection
client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
db = client['canteen_employee']
menu_collection = db['menus']
meal_preferences_collection = db['meal_preferences']

# Admin backend URL
ADMIN_BACKEND_URL = os.getenv('ADMIN_BACKEND_URL', 'http://localhost:5001')

def get_current_time():
    """Get current time in IST"""
    return datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')

# ============ HOME/WELCOME ROUTE ============

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Karmic Canteen Employee Backend API',
        'status': 'running',
        'version': '1.0',
        'timestamp': get_current_time(),
        'endpoints': {
            'health': 'GET /api/employee/health',
            'get_menu': 'GET /api/employee/menu/<date>',
            'save_preference': 'POST /api/employee/meal-preference',
            'get_preference': 'GET /api/employee/meal-preference/<employee_id>/<date>',
            'get_meal_counts': 'GET /api/employee/meal-counts/<date>'
        }
    }), 200


# ============ MENU SYNC (Receive from Admin) ============

@app.route('/api/employee/menu/sync', methods=['POST'])
def sync_menu():
    """Receive menu updates from admin backend"""
    try:
        data = request.json
        
        if not data or 'date' not in data:
            return jsonify({
                'success': False,
                'error': 'Date is required'
            }), 400
        
        menu_data = {
            'date': data.get('date'),
            'breakfast': data.get('breakfast', []),
            'lunch': data.get('lunch', []),
            'snacks': data.get('snacks', []),
            'updated_at': get_current_time()
        }
        
        # Store/update menu in employee database
        menu_collection.update_one(
            {'date': data.get('date')},
            {'$set': menu_data},
            upsert=True
        )
        
        return jsonify({
            'success': True,
            'message': 'Menu synced successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/employee/menu/<date>', methods=['GET'])
def get_menu(date):
    """Get menu for a specific date"""
    try:
        menu = menu_collection.find_one({'date': date}, {'_id': 0})
        
        if not menu:
            # Try to fetch from admin backend if not in local DB
            try:
                response = requests.get(
                    f'{ADMIN_BACKEND_URL}/api/admin/menu/{date}',
                    timeout=5
                )
                if response.status_code == 200:
                    admin_menu = response.json().get('menu')
                    if admin_menu:
                        # Cache it locally
                        menu_collection.insert_one(admin_menu)
                        return jsonify({
                            'success': True,
                            'menu': admin_menu,
                            'source': 'admin_backend'
                        }), 200
            except requests.exceptions.RequestException as e:
                print(f"Could not fetch from admin backend: {e}")
            
            return jsonify({
                'success': False,
                'message': 'Menu not found for this date'
            }), 404
            
        return jsonify({
            'success': True,
            'menu': menu,
            'source': 'local_cache'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/employee/menu/all', methods=['GET'])
def get_all_menus():
    """Get all menus"""
    try:
        menus = list(menu_collection.find({}, {'_id': 0}).sort('date', -1))
        
        return jsonify({
            'success': True,
            'count': len(menus),
            'menus': menus
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============ MEAL PREFERENCES ============

@app.route('/api/employee/meal-preference', methods=['POST'])
def save_meal_preference():
    """Employee selects which meals they want"""
    try:
        data = request.json
        
        if not data or 'employee_id' not in data or 'date' not in data:
            return jsonify({
                'success': False,
                'error': 'employee_id and date are required'
            }), 400
        
        preference_data = {
            'employee_id': data.get('employee_id'),
            'employee_name': data.get('employee_name', 'Unknown'),
            'date': data.get('date'),
            'breakfast': data.get('breakfast', False),
            'lunch': data.get('lunch', False),
            'snacks': data.get('snacks', False),
            'updated_at': get_current_time()
        }
        
        # Update or insert preference
        meal_preferences_collection.update_one(
            {
                'employee_id': data.get('employee_id'),
                'date': data.get('date')
            },
            {'$set': preference_data},
            upsert=True
        )
        
        # Calculate and send updated counts to admin
        update_meal_counts(data.get('date'))
        
        return jsonify({
            'success': True,
            'message': 'Meal preference saved successfully',
            'preference': preference_data
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/employee/meal-preference/<employee_id>/<date>', methods=['GET'])
def get_meal_preference(employee_id, date):
    """Get employee's meal preference for a specific date"""
    try:
        preference = meal_preferences_collection.find_one(
            {'employee_id': employee_id, 'date': date},
            {'_id': 0}
        )
        
        if not preference:
            return jsonify({
                'success': True,
                'preference': {
                    'employee_id': employee_id,
                    'date': date,
                    'breakfast': False,
                    'lunch': False,
                    'snacks': False
                }
            }), 200
            
        return jsonify({'success': True, 'preference': preference}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/employee/meal-preference/<employee_id>', methods=['GET'])
def get_employee_all_preferences(employee_id):
    """Get all preferences for an employee"""
    try:
        preferences = list(meal_preferences_collection.find(
            {'employee_id': employee_id},
            {'_id': 0}
        ).sort('date', -1))
        
        return jsonify({
            'success': True,
            'count': len(preferences),
            'preferences': preferences
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============ MEAL COUNT AGGREGATION ============

def update_meal_counts(date):
    """Calculate meal counts and send to admin backend"""
    try:
        # Aggregate counts for the date
        pipeline = [
            {'$match': {'date': date}},
            {'$group': {
                '_id': None,
                'breakfast_count': {
                    '$sum': {'$cond': ['$breakfast', 1, 0]}
                },
                'lunch_count': {
                    '$sum': {'$cond': ['$lunch', 1, 0]}
                },
                'snacks_count': {
                    '$sum': {'$cond': ['$snacks', 1, 0]}
                }
            }}
        ]
        
        result = list(meal_preferences_collection.aggregate(pipeline))
        
        if result:
            counts = result[0]
            count_data = {
                'breakfast_count': counts.get('breakfast_count', 0),
                'lunch_count': counts.get('lunch_count', 0),
                'snacks_count': counts.get('snacks_count', 0)
            }
        else:
            # No preferences yet, send zeros
            count_data = {
                'breakfast_count': 0,
                'lunch_count': 0,
                'snacks_count': 0
            }
        
        # Send to admin backend
        try:
            response = requests.post(
                f'{ADMIN_BACKEND_URL}/api/admin/meal-counts/{date}',
                json=count_data,
                timeout=5
            )
            print(f"Meal counts sent to admin: {count_data}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending meal counts to admin: {e}")
            
    except Exception as e:
        print(f"Error updating meal counts: {e}")


@app.route('/api/employee/meal-counts/<date>', methods=['GET'])
def get_local_meal_counts(date):
    """Get meal counts for a specific date (local calculation)"""
    try:
        pipeline = [
            {'$match': {'date': date}},
            {'$group': {
                '_id': None,
                'breakfast_count': {
                    '$sum': {'$cond': ['$breakfast', 1, 0]}
                },
                'lunch_count': {
                    '$sum': {'$cond': ['$lunch', 1, 0]}
                },
                'snacks_count': {
                    '$sum': {'$cond': ['$snacks', 1, 0]}
                }
            }}
        ]
        
        result = list(meal_preferences_collection.aggregate(pipeline))
        
        if result:
            counts = result[0]
            return jsonify({
                'success': True,
                'counts': {
                    'date': date,
                    'breakfast_count': counts.get('breakfast_count', 0),
                    'lunch_count': counts.get('lunch_count', 0),
                    'snacks_count': counts.get('snacks_count', 0)
                }
            }), 200
        else:
            return jsonify({
                'success': True,
                'counts': {
                    'date': date,
                    'breakfast_count': 0,
                    'lunch_count': 0,
                    'snacks_count': 0
                }
            }), 200
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/employee/preferences/date/<date>', methods=['GET'])
def get_all_preferences_by_date(date):
    """Get all employee preferences for a specific date"""
    try:
        preferences = list(meal_preferences_collection.find(
            {'date': date},
            {'_id': 0}
        ))
        
        return jsonify({
            'success': True,
            'count': len(preferences),
            'preferences': preferences
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============ HEALTH CHECK ============

@app.route('/api/employee/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'employee-backend',
        'timestamp': get_current_time(),
        'database': 'connected' if client.server_info() else 'disconnected'
    }), 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True)