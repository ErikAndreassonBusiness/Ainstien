# app/__init__.py

"""
This file initializes the Flask application and sets up its core configuration.
It serves as the package constructor for the 'app' directory, linking the 
database (SQLAlchemy) to the Flask instance, configuring the SQLite URI, 
and ensuring all database tables are created within the application context.
"""

from flask import Flask
from .server.database import db
import os

def create_app():
    app = Flask(__name__,
            template_folder='templates',
            static_folder='static')

    
    # ===== Configure the database =======
    basedir = os.path.abspath(os.path.dirname(__file__))

    data_folder = os.path.join(basedir, '../data') #go to the data folder
    if not os.path.exists(data_folder): #if not exists, create one
        os.makedirs(data_folder)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(data_folder, 'company.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app) #Connect the app woth the database

    # create the database
    with app.app_context():
        from .server import routes
        db.create_all()  

    return app