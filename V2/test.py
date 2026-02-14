
import requests
def Coinmarket( Crypto_Name):  # <-- self اضافه شد

    API_KEY_coinmarket = "07af61ff-8f34-47ea-8f5e-94f161861357"

    if not API_KEY_coinmarket:
        raise ValueError("API Key is empty")

    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    params = {"symbol": Crypto_Name, "convert": "USD"}
    headers = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": API_KEY_coinmarket}

    response = requests.get(url, headers=headers, params=params, timeout=10)
    if response.status_code != 200:
        print(response.text)  # برای دیدن دلیل واقعی
    response.raise_for_status()

    data = response.json()
    return data["data"][Crypto_Name]["quote"]["USD"]["price"]



btc_price = Coinmarket("BTC")
ton_price = Coinmarket("TON")


print(btc_price)