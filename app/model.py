from database import db, Company

def print_stock_info():
    print(db.session.get(Company, 1).serialize())