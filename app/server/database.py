from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date

db = SQLAlchemy() 

class Company(db.Model): 
    __tablename__ = "company"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(unique=True, nullable=False)
    #borsdata_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=True)

     # ==== Connections to other entities ====
    annual_reports: Mapped[list['Annual_Report']] = relationship(back_populates='company')
    quarterly_reports: Mapped[list['Quarterly_Report']] = relationship(back_populates='company')

class Annual_Report(db.Model): 
    __tablename__ = "annual_report"
    id: Mapped[int] = mapped_column(primary_key=True)
    report_date: Mapped[date] = mapped_column(nullable=False)

    # ==== For our predictions =====
    share_outstanding: Mapped[int] = mapped_column(nullable=False)

    current_price : Mapped[float] = mapped_column(nullable=False)
    one_month_price : Mapped[float] = mapped_column(nullable=False)
    two_month_price : Mapped[float] = mapped_column(nullable=False)
    three_month_price : Mapped[float] = mapped_column(nullable=False)

    max_average_future_price: Mapped[float] = mapped_column(nullable=False) #y (Target), currently 3 months

    # ==== Connections to other entities ====
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'), nullable=False)
    company: Mapped["Company"] = relationship(back_populates='annual_reports')

    fundamental_id: Mapped[int] = mapped_column(ForeignKey('fundamental.id'), nullable=True)
    fundamental: Mapped["Fundamental"] = relationship(
        cascade="all, delete-orphan", 
        single_parent=True)

    metric_id: Mapped[int] = mapped_column(ForeignKey('metric.id'), nullable=True) #Not requiered for the first report
    metric: Mapped["Metric"] = relationship(
        cascade="all, delete-orphan", 
        single_parent=True)

    def to_dict(self):
        return {
            "id": self.id,
            "report_date": self.report_date.isoformat(),  # Converts date object to "YYYY-MM-DD" string
            "fundamentals": self.fundamental.to_dict() if self.fundamental else None,
            "metrics": self.metric.to_dict() if self.metric else None
        }

class Quarterly_Report(db.Model): 
    __tablename__ = "quarterly_report"
    id: Mapped[int] = mapped_column(primary_key=True)
    report_date: Mapped[date] = mapped_column(nullable=False)

    # ==== For our predictions =====
    share_outstanding: Mapped[int] = mapped_column(nullable=False)

    current_price : Mapped[float] = mapped_column(nullable=False)
    one_month_price : Mapped[float] = mapped_column(nullable=False)
    two_month_price : Mapped[float] = mapped_column(nullable=False)
    three_month_price : Mapped[float] = mapped_column(nullable=False)

    max_average_future_price: Mapped[float] = mapped_column(nullable=False) #y (Target), currently 3 months

    # ==== Connections to other entities ====
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'), nullable=False)
    company: Mapped["Company"] = relationship(back_populates='quarterly_reports')

    fundamental_id: Mapped[int] = mapped_column(ForeignKey('fundamental.id'), nullable=True)
    fundamental: Mapped["Fundamental"] = relationship(cascade="all, delete-orphan", single_parent=True)

    metric_id: Mapped[int] = mapped_column(ForeignKey('metric.id'), nullable=True) #Not requiered for the first report
    metric: Mapped["Metric"] = relationship(cascade="all, delete-orphan", single_parent=True)


    def to_dict(self):
        return {
            "id": self.id,
            "report_date": self.report_date.isoformat(),  # Converts date object to "YYYY-MM-DD" string
            "fundamentals": self.fundamental.to_dict() if self.fundamental else None,
            "metrics": self.metric.to_dict() if self.metric else None
        }

class Fundamental(db.Model): #4 år bak
    __tablename__ = "fundamental"
    id: Mapped[int] = mapped_column(primary_key=True)

    # substansvarde: Mapped[float] = mapped_column(nullable=False)

    # ======== Income Statement (MSEK???) ========
    revenue: Mapped[float] = mapped_column(nullable=False)
    depreciation: Mapped[float] = mapped_column(nullable=False)
    ebitda: Mapped[float] = mapped_column(nullable=False)
    ebit: Mapped[float] = mapped_column(nullable=False)
    net_income: Mapped[float] = mapped_column(nullable=False)

    # ========= Balance Sheet (MSEK???) ==========
    total_assets: Mapped[float] = mapped_column(nullable=False)
    total_equity: Mapped[float] = mapped_column(nullable=False)

    # Total debt, Sum(): 
    total_debt: Mapped[float] = mapped_column(nullable=False)
    short_term_debt: Mapped[float] = mapped_column(nullable=False)
    long_term_debt: Mapped[float] = mapped_column(nullable=False)

    # Omsättningstillgångar
    current_assets: Mapped[float] = mapped_column(nullable=False)
    inventory: Mapped[float] = mapped_column(nullable=False)
    account_receivables: Mapped[float] = mapped_column(nullable=False)
    cash: Mapped[float] = mapped_column(nullable=False)

    # Anläggsningstillgångar
    fixed_assets: Mapped[float] = mapped_column(nullable=False)

    def to_dict(self): 
        return {
            "revenue": self.revenue,
            "depreciation": self.depreciation,
            "ebitda": self.ebitda,
            "ebit": self.ebit,
            "net_income": self.net_income,
            "total_assets": self.total_assets,
            "total_equity": self.total_equity,
            "short_term_debt": self.short_term_debt, 
            "long_term_debt": self.long_term_debt,
            "total_debt": self.total_debt,
            "current_assets": self.current_assets,
            "fixed_assets": self.fixed_assets,
            "cash": self.cash,
            "inventory": self.inventory,
            "account_receivables": self.account_receivables
        }

    @classmethod
    def get_attribute_names(cls):
        ignored_keys = {'id', 'report_id'}
        return [col.key.lower() for col in cls.__table__.columns if col.key not in ignored_keys]

class Metric(db.Model):
    __tablename__ = "metric"
    id: Mapped[int] = mapped_column(primary_key=True)

    """ ========================== Growth ratios ======================= """
    #Omsättningstillväxt (%)
    revenue_growth_percent: Mapped[float] = mapped_column(nullable=False)

    #Vinsttillväxt (%)
    profit_growth_percent: Mapped[float] = mapped_column(nullable=False)
    
    """ ================ Liquidity ratios: Short-term payment ability =========== """
    # Kassalikviditet (%)
    quick_ratio_percent: Mapped[float] = mapped_column(nullable=False) # Omsättningstillgånger - Varulager +  Pågående arbete / Kortfirstiga skulder

    # Nettoskuld / EBITDA
    net_debt_ebitda_ratio: Mapped[float] = mapped_column(nullable=False) # (Räntebärande skulder) / EBITDA

    """ =============== Leverage ratios: Debt and capital structure ============="""
    #Soliditet (%)
    equity_ratio_percent: Mapped[float] = mapped_column(nullable=False) # Tot. Equtiy / Tot. Assests

    """ ============== Efficiency ratios: Asset use and productivity ============= """
    #Kaptialomsättningshastighet (ggr)
    assets_turnover_ratio: Mapped[float] = mapped_column(nullable=False) #Sales / Tot. Average Assets

    #Varulagersomsättningshastighet (ggr)
    inventory_turnover_ratio : Mapped[float] = mapped_column(nullable=False) # Cost of Goods Sold / Average Inventory 

    # Return on Assets
    roa : Mapped[float] = mapped_column(nullable=False) #Net Income / Tot. Average Assets 

    #Return on Equtiy
    roe : Mapped[float] = mapped_column(nullable=False) #Net Income / Avarage Shareholders' Equity

    #Return on Investment
    roi : Mapped[float] = mapped_column(nullable=False) #Net Income from Investment / Cost of Investment

    """ ============== Profitability ratios: Profit relative to sales, assets, or equity ============= """
    ebit_margin_percent: Mapped[float] = mapped_column(nullable=False)
    profit_margin_percent: Mapped[float] = mapped_column(nullable=False)

    def to_dict(self):
        return {
            "revenue_growth_percent": self.revenue_growth_percent, 
            "profit_growth_percent": self.profit_growth_percent, 
            "quick_ratio_percent": self.quick_ratio_percent,
            "net_debt_ebitda_ratio": self.net_debt_ebitda_ratio,
            "equity_ratio_percent": self.equity_ratio_percent,
            "assets_turnover_ratio": self.assets_turnover_ratio,
            "inventory_turnover_ratio": self.inventory_turnover_ratio,
            "roa": self.roa,
            "roe": self.roe,
            "roi": self.roi,
            "ebit_margin_percent": self.ebit_margin_percent,
            "profit_margin_percent": self.profit_margin_percent
        }

    @classmethod
    def get_attribute_names(cls):
        ignored_keys = {'id', 'report_id'}
        return [col.key.lower() for col in cls.__table__.columns if col.key not in ignored_keys]