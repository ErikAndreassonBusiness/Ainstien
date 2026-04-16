"""
app/database.py
Purpose: Defines the SQLAlchemy database object and the data models (tables).
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy() #Initialize db 

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100))
    fundamentals = db.relationship('Fundamental', backref='company', lazy=True)

class Fundamental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    report_date = db.Column(db.Date, nullable=False)
    revenue = db.Column(db.Float)
    net_income = db.Column(db.Float)
    eps = db.Column(db.Float)