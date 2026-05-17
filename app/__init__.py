from flask import Flask
from flask_cors import CORS

from app.config.settings import Config
from app.database.db import db
from app.bootstrap.startup import initialize_database
from app.controllers.print_controller import print_bp

def create_app():
    app = Flask(__name__)
    
    app.config.from_object(Config)
    
    CORS(app)
    
    db.init_app(app)
    
    app.register_blueprint(print_bp)
    
    from app.models import Empleado, Registro
    
    with app.app_context():
        initialize_database()
    
    return app