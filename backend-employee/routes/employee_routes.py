from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.employee_service import EmployeeService
from datetime import datetime, timedelta

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/register', methods=['POST'])
def register():
    """Register new employee"""
    data = request.get_json()
    
    required_fields = ['employee_id', 'name', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    employee, error = EmployeeService.register_employee(
        employee_id=data['employee_id'],
        name=data['name'],
        email=data['email'],
        password=data['password'],
        department=data.get('department', '')
    )
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Employee registered successfully',
        'employee': employee.to_dict()
    }), 201


@employee_bp.route('/login', methods=['POST'])
def login():
    """Employee login"""
    data = request.get_json()
    
    if not data.get('employee_id') or not data.get('password'):
        return jsonify({'error': 'Employee ID and password required'}), 400
    
    result, error = EmployeeService.login_employee(
        employee_id=data['employee_id'],
        password=data['password']
    )
    
    if error:
        return jsonify({'error': error}), 401
    
    return jsonify(result), 200


@employee_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get employee profile"""
    employee_id = get_jwt_identity()
    
    profile, error = EmployeeService.get_employee_profile(int(employee_id))
    
    if error:
        return jsonify({'error': error}), 404
    
    return jsonify(profile), 200


@employee_bp.route('/menu', methods=['GET'])
@jwt_required()
def get_menu():
    """Get daily menu for tomorrow"""
    date_str = request.args.get('date')
    
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    else:
        date = (datetime.now() + timedelta(days=1)).date()
    
    menu, error = EmployeeService.get_daily_menu(date)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'date': date.isoformat(),
        'menu': menu
    }), 200


@employee_bp.route('/meal/confirm', methods=['POST'])
@jwt_required()
def confirm_meal():
    """Confirm meal selection"""
    employee_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['date', 'meal_type', 'menu_item_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        date = datetime.strptime(data['date'], '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    result, error = EmployeeService.confirm_meal(
        employee_id=int(employee_id),
        date=date,
        meal_type=data['meal_type'],
        menu_item_id=data['menu_item_id']
    )
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify(result), 200


@employee_bp.route('/meal/cancel', methods=['POST'])
@jwt_required()
def cancel_meal():
    """Cancel meal selection"""
    employee_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['date', 'meal_type']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        date = datetime.strptime(data['date'], '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    result, error = EmployeeService.cancel_meal(
        employee_id=int(employee_id),
        date=date,
        meal_type=data['meal_type']
    )
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify(result), 200


@employee_bp.route('/selections', methods=['GET'])
@jwt_required()
def get_selections():
    """Get employee's meal selections"""
    employee_id = get_jwt_identity()
    
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    start_date = None
    end_date = None
    
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid start_date format'}), 400
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid end_date format'}), 400
    
    selections, error = EmployeeService.get_my_selections(
        employee_id=int(employee_id),
        start_date=start_date,
        end_date=end_date
    )
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({'selections': selections}), 200