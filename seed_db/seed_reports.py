

def get_stage_report(new_company, report_dates, ticker_data, inc, bal): 
    """ Stages one report in COMPANIES_TO_COMMIT list """

    for date in report_dates:
         # --- Calulcate price when report is published ---
        end_date = date + timedelta(days=5) # handeling holidays
        start_str = date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')

        report_date_prices = ticker_obj.history(
            start=start_str, 
            end=end_str, 
            interval="1d")
        
        for price in report_date_prices:
            if not(price is None or price == 'Nan'): 
                close_price = price['Close']
                break
        
        # --- Calculate max_avarage price ---
        start_date  = date + timedelta(days = 90) # 3 months
        end_date = start_date + timedelta(days = 5)

        max_prices = ticker_obj.history(
            start=start_str, 
            end=end_str, 
            interval="1d")
        
        prices_to_avarage = []
        for price in max_prices:
            if not(price is None or price == 'Nan'): 
                prices_to_avarage.append(price['Close'])

        sum_prices = 0
        for price in prices_to_avarage: 
            sum_prices = sum_prices + price
        
        avarage_prices = sum_prices / len(prices_to_avarage)

        new_report = Report(
            report_date = date,
            share_outstanding = 10000000,
            current_price = close_price,
            max_average_future_price = avarage_prices,
            company_id = new_company.id, 
        )

        return new_report