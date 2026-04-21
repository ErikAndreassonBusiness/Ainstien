"""
app/database.py
Purpose: Defines the SQLAlchemy database object and the data models (tables).
Structure:
Company - Fundamental (one-to-one relationship)
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date

db = SQLAlchemy() #Initialize db 

class Company(db.Model):
    __tablename__ = "company"
    id : Mapped[int] = mapped_column(primary_key=True)
    ticker : Mapped[str] = mapped_column(unique=True, nullable=False)
    name : Mapped[str] = mapped_column()
    fundamentals: Mapped['Fundamental'] = relationship(back_populates='company', )

class Fundamental(db.Model):
    __tablename__ = "fundamental"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'), unique=True, nullable=False)

    company : Mapped['Company'] = relationship(back_populates='fundamentals')

    report_date: Mapped[date] = mapped_column(nullable=False)
    revenue: Mapped[float] = mapped_column()
    net_income: Mapped[float] = mapped_column()
    eps: Mapped[float] = mapped_column()