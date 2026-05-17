from flask import Flask
from flask_cors import CORS

from app.config.settings import Config
from app.database.db import db
from app.bootstrap.startup import initialize_database

def create_app():
    app = Flask(__name__)
    
    app.config.from_object(Config)
    
    CORS(app)
    
    db.init_app(app)
    
    from app.models import Empleado, Registro
    
    with app.app_context():
        db.create_all()
    
    return app