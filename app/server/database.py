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

     # ==== Connections to other entities ====
    reports: Mapped[list['Report']] = relationship(back_populates='company')

class Report(db.Model): 
    __tablename__ = "report"
    id: Mapped[int] = mapped_column(primary_key=True)
    report_date: Mapped[date] = mapped_column(nullable=False)

    # ==== For our predictions =====
    share_outstanding: Mapped[int] = mapped_column(nullable=False)
    current_price : Mapped[float] = mapped_column(nullable=False)
    max_average_future_price: Mapped[float] = mapped_column(nullable=False) #y (Target), currently 3 months

    # ==== Connections to other entities ====
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'), nullable=False)
    company: Mapped["Company"] = relationship(back_populates='reports')

    # Relationship (delete-orphan: Om report tas bort, tas även fundementals och metrics bort)
    fundamental: Mapped["Fundamental"] = relationship(back_populates='report', cascade="all, delete-orphan")
    metric: Mapped["Metric"] = relationship(back_populates='report', cascade="all, delete-orphan")

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

    report_id: Mapped[int] = mapped_column(ForeignKey('report.id'), nullable=False)
    report: Mapped["Report"] = relationship(back_populates='fundamental')

    # substansvarde: Mapped[float] = mapped_column(nullable=False)

    # ======== Income Statement (MSEK???) ========
    revenue: Mapped[float] = mapped_column(nullable=False)
    depreciation: Mapped[float] = mapped_column(nullable=False)
    EBITDA: Mapped[float] = mapped_column()
    EBIT: Mapped[float] = mapped_column()
    net_income: Mapped[float] = mapped_column()

    # ========= Balance Sheet (MSEK???) ==========
    total_assets: Mapped[float] = mapped_column()
    total_equity: Mapped[float] = mapped_column()

    # Total debt, Sum(): 
    total_debt: Mapped[float] = mapped_column()
    short_term_debt: Mapped[float] = mapped_column()
    long_term_debt: Mapped[float] = mapped_column()

    # Omsättningstillgångar
    current_assets: Mapped[float] = mapped_column()
    inventory: Mapped[float] = mapped_column()
    account_receiveables: Mapped[float] = mapped_column()
    cash: Mapped[float] = mapped_column()

    # Anläggsningstillgångar
    fixed_assets: Mapped[float] = mapped_column()
    goodwill: Mapped[float] = mapped_column()

    def get_attribute_dict(self): 
        return {
            "revenue": self.revenue,
            "depreciation": self.depreciation,
            "ebitda": self.EBITDA,
            "ebit": self.EBIT,
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
            "account_receiveables": self.account_receiveables
        }

    @classmethod
    def get_attribute_names(cls):
        ignored_keys = {'id', 'report_id'}
        return [col.key for col in cls.__table__.columns if col.key not in ignored_keys]

    def to_dict(self):
        return self.get_attribute_dict()

class Metric(db.Model):
    __tablename__ = "metric"
    id: Mapped[int] = mapped_column(primary_key=True)

    report_id: Mapped[int] = mapped_column(ForeignKey('report.id'), nullable=False)
    report: Mapped["Report"] = relationship(back_populates='metric')

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
    ROA : Mapped[float] = mapped_column(nullable=False) #Net Income / Tot. Average Assets 

    #Return on Equtiy
    ROE : Mapped[float] = mapped_column(nullable=False) #Net Income / Avarage Shareholders' Equity

    #Return on Investment
    ROI : Mapped[float] = mapped_column(nullable=False) #Net Income from Investment / Cost of Investment

    """ ============== Profitability ratios: Profit relative to sales, assets, or equity ============= """
    #gross_profit_margin_percent: Mapped[float] = mapped_column(nullable=False)
    ebit_margin_percent: Mapped[float] = mapped_column(nullable=False)
    profit_margin_percent: Mapped[float] = mapped_column(nullable=False)

    def get_attribute_dict(self):
        return {
            "revenue_growth_percent": self.revenue_growth_percent, 
            "profit_growth_percent": self.profit_growth_percent, 
            "quick_ratio_percent": self.quick_ratio_percent,
            "net_debt_ebitda_ratio": self.net_debt_ebitda_ratio,
            "equity_ratio_percent": self.equity_ratio_percent,
            "assets_turnover_ratio": self.assets_turnover_ratio,
            "inventory_turnover_ratio": self.inventory_turnover_ratio,
            "roa": self.ROA,
            "roe": self.ROE,
            "roi": self.ROI,
            "ebit_margin_percent": self.ebit_margin_percent,
            "profit_margin_percent": self.profit_margin_percent
        }

    @classmethod
    def get_attribute_names(cls):
        ignored_keys = {'id', 'report_id'}
        return [col.key for col in cls.__table__.columns if col.key not in ignored_keys]

    def to_dict(self):
        return self.get_attribute_dict()