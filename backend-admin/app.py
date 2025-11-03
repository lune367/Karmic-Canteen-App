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
db = client['canteen_admin']
menu_collection = db['menus']
meal_counts_collection = db['meal_counts']

# Employee backend URL
EMPLOYEE_BACKEND_URL = os.getenv('EMPLOYEE_BACKEND_URL', 'http://localhost:5002')

def get_current_time():
    """Get current time in IST"""
    return datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')

# ============ HOME/WELCOME ROUTE ============

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Karmic Canteen Admin Backend API',
        'status': 'running',
        'version': '1.0',
        'timestamp': get_current_time(),
        'endpoints': {
            'health': 'GET /api/admin/health',
            'create_menu': 'POST /api/admin/menu',
            'get_menu': 'GET /api/admin/menu/<date>',
            'update_menu': 'PUT /api/admin/menu/<date>',
            'delete_menu': 'DELETE /api/admin/menu/<date>',
            'get_meal_counts': 'GET /api/admin/meal-counts/<date>',
            'get_meal_counts_range': 'GET /api/admin/meal-counts/range?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD'
        }
    }), 200


# ============ MENU MANAGEMENT ============

@app.route('/api/admin/menu', methods=['POST'])
def create_menu():
    """Create or update menu for a specific date"""
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
        
        # Upsert menu (update if exists, insert if not)
        menu_collection.update_one(
            {'date': data.get('date')},
            {'$set': menu_data},
            upsert=True
        )
        
        # Notify employee backend about menu update
        try:
            response = requests.post(
                f'{EMPLOYEE_BACKEND_URL}/api/employee/menu/sync',
                json=menu_data,
                timeout=5
            )
            sync_status = 'synced' if response.status_code == 200 else 'sync_failed'
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not sync with employee backend: {e}")
            sync_status = 'sync_failed'
        
        return jsonify({
            'success': True,
            'message': 'Menu created/updated successfully',
            'menu': menu_data,
            'sync_status': sync_status
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/menu/<date>', methods=['GET'])
def get_menu(date):
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


@app.route('/api/admin/menu/all', methods=['GET'])
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


@app.route('/api/admin/menu/<date>', methods=['PUT'])
def update_menu(date):
    """Update existing menu"""
    try:
        data = request.json
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        update_data = {
            'breakfast': data.get('breakfast'),
            'lunch': data.get('lunch'),
            'snacks': data.get('snacks'),
            'updated_at': get_current_time()
        }
        
        result = menu_collection.update_one(
            {'date': date},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({
                'success': False,
                'message': 'Menu not found for this date'
            }), 404
        
        # Notify employee backend
        try:
            response = requests.post(
                f'{EMPLOYEE_BACKEND_URL}/api/employee/menu/sync',
                json={'date': date, **update_data},
                timeout=5
            )
            sync_status = 'synced' if response.status_code == 200 else 'sync_failed'
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not sync with employee backend: {e}")
            sync_status = 'sync_failed'
        
        return jsonify({
            'success': True,
            'message': 'Menu updated successfully',
            'sync_status': sync_status
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/menu/<date>', methods=['DELETE'])
def delete_menu(date):
    """Delete menu for a specific date"""
    try:
        result = menu_collection.delete_one({'date': date})
        
        if result.deleted_count == 0:
            return jsonify({
                'success': False,
                'message': 'Menu not found for this date'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Menu deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============ MEAL COUNT TRACKING ============

@app.route('/api/admin/meal-counts/<date>', methods=['POST'])
def receive_meal_counts(date):
    """Receive meal count updates from employee backend"""
    try:
        data = request.json
        
        count_data = {
            'date': date,
            'breakfast_count': data.get('breakfast_count', 0),
            'lunch_count': data.get('lunch_count', 0),
            'snacks_count': data.get('snacks_count', 0),
            'updated_at': get_current_time()
        }
        
        meal_counts_collection.update_one(
            {'date': date},
            {'$set': count_data},
            upsert=True
        )
        
        return jsonify({
            'success': True,
            'message': 'Meal counts updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/meal-counts/<date>', methods=['GET'])
def get_meal_counts(date):
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
def get_meal_counts_range():
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


@app.route('/api/admin/meal-counts/all', methods=['GET'])
def get_all_meal_counts():
    """Get all meal counts"""
    try:
        counts = list(meal_counts_collection.find({}, {'_id': 0}).sort('date', -1))
        
        return jsonify({
            'success': True,
            'count': len(counts),
            'counts': counts
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============ HEALTH CHECK ============

@app.route('/api/admin/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'admin-backend',
        'timestamp': get_current_time(),
        'database': 'connected' if client.server_info() else 'disconnected'
    }), 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)