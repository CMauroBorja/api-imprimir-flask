from flask import Flask
from flask_cors import CORS
from app.config.settings import Config
from app.database.db import db
from app.bootstrap.startup import initialize_database
from app.controllers.print_controller import print_bp
from app.controllers.employee_controller import employee_bp
from app.controllers.auth_controller import auth_bp
from app.controllers.order_controller import order_bp
from app.exceptions.handlers import register_error_handlers

def create_app():
    app = Flask(__name__)
    
    app.config.from_object(Config)
    
    CORS(app)
    
    db.init_app(app)
    
    app.register_blueprint(print_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(order_bp)
    
    register_error_handlers(app)
    
    with app.app_context():
        initialize_database()
    
    return app