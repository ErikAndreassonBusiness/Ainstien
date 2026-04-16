# app/__init__.py

"""
This file initializes the Flask application and sets up its core configuration.
It serves as the package constructor for the 'app' directory, linking the 
database (SQLAlchemy) to the Flask instance, configuring the SQLite URI, 
and ensuring all database tables are created within the application context.
"""

from flask import Flask
from .database import db
import os

def create_app():
    app = Flask(__name__)
    
    # Configure SQLite
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '../data/trading.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()  # This creates the .db file and tables automatically

    return app