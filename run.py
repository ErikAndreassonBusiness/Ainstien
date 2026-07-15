from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    # # Access the variable directly from your environment
    # api_key = os.getenv("Alpha_Vantage_API_key")

    # import requests

    # # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
    # url = f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol=VOLV-B.ST&apikey={api_key}'
    # r = requests.get(url)
    # data = r.json()

    # print(data)
    app.run(port=5001, debug=True)