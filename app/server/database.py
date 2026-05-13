from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date

db = SQLAlchemy() 

class Company(db.Model):
    __tablename__ = "company"
    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=True)

    fundamentals: Mapped[list['Fundamental']] = relationship(back_populates='company') #1:M
    metrics: Mapped[list['Metrics']] = relationship(back_populates='company') #1:M

    def serialize_company_info(self): 
        return {
            "id": self.id,
            "name": self.name,
            "ticker": self.ticker
        }

    # Serialize the fundamental_list 
    def serialize_fundamentals_list(self): 
        fundamental_list = []
        for fundamental in self.fundamentals: 
            fundamental_list.append(fundamental.serialize())
        return fundamental_list

    def serialize_company_and_fundementals(self):
        return {
            "id": self.id,
            "name": self.name,
            "ticker": self.ticker,
            "fundamentals": self.serialize_fundamentals_list() 
        }

class Fundamental(db.Model):
    __tablename__ = "fundamental"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'), nullable=False)

    company: Mapped['Company'] = relationship(back_populates='fundamentals')

    report_date: Mapped[date] = mapped_column(nullable=False)
    revenue: Mapped[float] = mapped_column(nullable=False)
    net_income: Mapped[float] = mapped_column(nullable=False)

    revenue_growth_percent: Mapped[float] = mapped_column(nullable=False)
    profit_growth_percent: Mapped[float] = mapped_column(nullable=False)
    ebit_margin_percent: Mapped[float] = mapped_column(nullable=False)
    soliditet_percent: Mapped[float] = mapped_column(nullable=False)

    def serialize_fundamental_info(self): 
        return [
            self.revenue, 
            self.net_income,
            self.revenue_growth_percent, 
            self.profit_growth_percent, 
            self.ebit_margin_percent, 
            self.soliditet_percent
        ]
    
    def serialize(self):
        return {
            "company_id": self.company_id,
            "report_date": self.report_date.isoformat(),
            "revenue": self.revenue, 
            "net_income": self.net_income,
            "revenue_growth_percent": self.revenue_growth_percent, 
            "profit_growth_percent": self.profit_growth_percent, 
            "ebit_margin_percent": self.ebit_margin_percent, 
            "soliditet_percent": self.soliditet_percent
        }

    class Metrics(db.Model):
        __tablename__ = "metrics"
        id: Mapped[int] = mapped_column(primary_key=True)
        company_id: Mapped[int] = mapped_column(ForeignKey('company.id'), nullable=False)
        company: Mapped['Company'] = relationship(back_populates='metrics')

        """ ========================== Growth ratios ======================= """
        #Omsättningstillväxt (%)
        revenue_growth_percent: Mapped[float] = mapped_column(nullable=False)

        #Vinsttillväxt (%)
        profit_growth_percent: Mapped[float] = mapped_column(nullable=False)
        
        """ ================ Liquidity ratios: Short-term payment ability =========== """
        #Kassalikviditet (%)
        quick_ratio_percent: Mapped[float] = mapped_column(nullable=False) # Omsättningstillgånger - Varulager +  Pågående arbete / Kortfirstiga skulder

        """ =============== Leverage ratios: Debt and capital structure ============="""
        #Soliditet (%)
        equity_ratio_percent: Mapped[float] = mapped_column(nullable=False) # Tot. Equtiy / Tot. Assests

        """ ============== Efficiency ratios: Asset use and productivity ============= """
        #Kaptialomsättningshastighet (ggr)
        assets_turnover_ratio: Mapped[float] = mapped_column(nullable=False) #Sales / Tot. Average Assets

        #Varulagersomsättningshastighet (ggr)
        inventory_turnover_ratio : Mapped[float] = mapped_column(nullable=False) # Cost of Goods Sold / Average Inventory 

        # Return on Assets
        ROA : Mapped[float] = mapped_column(nullable=False) #Net Income / Tot. Average Assets 

        #Return on Equtiy
        ROE : Mapped[float] = mapped_column(nullable=False) #Net Income / Avarage Shareholders' Equity

        #Return on Investment
        ROI : Mapped[float] = mapped_column(nullable=False) #Net Income from Investment / Cost of Investment

        """ ============== Profitability ratios: Profit relative to sales, assets, or equity ============= """
        gross_profit_margin_percent: Mapped[float] = mapped_column(nullable=False)
        ebit_margin_percent: Mapped[float] = mapped_column(nullable=False)
        profit_margin_percent: Mapped[float] = mapped_column(nullable=False)

        

