import requests

def credits_left(api_key):
    url = "https://pro-api.coinmarketcap.com/v1/key/info"
    headers = {"X-CMC_PRO_API_KEY": api_key}

    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()["data"]["usage"]["current_month"]["credits_left"]


# استفاده
api_key = "07af61ff-8f34-47ea-8f5e-94f161861357"
print("Credits left:", credits_left(api_key))