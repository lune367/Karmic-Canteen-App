from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
jwt = JWTManager()
app = Flask(__name__)

def create_app():
    
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Register blueprints
    from routes.employee_routes import employee_bp
    app.register_blueprint(employee_bp, url_prefix='/api/employee')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    @app.route('/')
    def index():
        return {'message': 'Karmic Canteen API - Employee Module', 'status': 'running'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True,host='0.0.0.0', port=5000)