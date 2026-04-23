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
    name : Mapped[str] = mapped_column(nullable = True)
    fundamentals: Mapped[list['Fundamental']] = relationship(back_populates='company', )

class Fundamental(db.Model):
    __tablename__ = "fundamental"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'), nullable=False)

    company : Mapped['Company'] = relationship(back_populates='fundamentals')

    report_date: Mapped[date] = mapped_column(nullable=False)
    revenue: Mapped[float] = mapped_column(nullable=False)
    net_income: Mapped[float] = mapped_column(nullable=False)

    revenue_growth_percent: Mapped[float] = mapped_column(nullable=False)
    profit_growth_percent: Mapped[float] = mapped_column(nullable=False)
    ebit_margin_percent: Mapped[float] = mapped_column(nullable=False)
    soliditet_percent: Mapped[float] = mapped_column(nullable=False)
    #net_debt_ebitda: Mapped[float] = mapped_column(nullable=False)