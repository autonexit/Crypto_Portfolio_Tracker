import requests
import csv
import os
from datetime import date
from datetime import datetime

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile


today = date.today()

# Coinmarket API
def Coinmarket(Crypto_Name):
    API_KEY_coinmarket = "07af61ff-8f34-47ea-8f5e-94f161861357"

    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    params = {"symbol": Crypto_Name, "convert": "USD"}
    headers = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": API_KEY_coinmarket}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data["data"][Crypto_Name]["quote"]["USD"]["price"]
    except Exception as e:
        print("Coinmarket error:", e)
        return 0.0


BTC_Price = Coinmarket('BTC')
ton_price = Coinmarket('TON')

USDT_Price_Now = 0.0
window = None


def calculate_prog():
    global USDT_Price_Now

    # ===== Read from Qt widgets (NEW objectNames) =====
    USDT_Price_Now = float(window.usdtEntry.text())
    Crypto_User = float(window.amountEntry.text())

    Crypto_User_Price = 0.0

    if Crypto_User > 0:
        Symbol_User = str(window.symbolEntry.text()).strip().upper()
        USDT_User = float(window.usdBuyEntry.text())

        if Symbol_User == "BTC":
            Crypto_User_Price = BTC_Price
        elif Symbol_User == "TON":
            Crypto_User_Price = ton_price

    file_path = "prices.csv"
    file_exists = os.path.exists(file_path)

    with open(file_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if (not file_exists) or (os.path.getsize(file_path) == 0):
            writer.writerow(["user_value", "price", "USD Price", "symbol", "Date"])
        if Crypto_User > 0:
            writer.writerow([Crypto_User, Crypto_User_Price, USDT_User, Symbol_User, today])

    def user_profit(row_number_in_file):
        with open("prices.csv", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for index, row in enumerate(reader, start=2):
                if index == row_number_in_file:
                    try:
                        User_Value_Get = float(row["user_value"])
                        User_Price_Get = float(row["price"])
                        user_usdt_price = float(row["USD Price"])
                        user_symbol_Get = row["symbol"]
                        user_date_Get = row["Date"]
                    except:
                        return 0, None, None, None
                    break
            else:
                return 0, None, None, None

        User_Buy_Price = User_Value_Get * User_Price_Get * user_usdt_price

        if user_symbol_Get == "BTC":
            Crypto_Price_Target = BTC_Price
        elif user_symbol_Get == "TON":
            Crypto_Price_Target = ton_price
        else:
            return 0, None, None, None

        Price_Now = User_Value_Get * Crypto_Price_Target * USDT_Price_Now

        user_date_Get_Nformat = datetime.strptime(user_date_Get, "%Y-%m-%d").date()
        duration = today - user_date_Get_Nformat

        profit = Price_Now - User_Buy_Price
        return profit, user_symbol_Get, Price_Now, duration.days


    # ===== Output to Qt TextEdit =====
    window.resultBox.clear()

    Total_profit = 0.0
    for i in range(1, 100):
        profit, symboll, Assets_Price, days_passed = user_profit(i)
        Total_profit += profit
        if profit != 0 and symboll is not None:
            window.resultBox.append(
                f"Row {i} | {symboll} | Profit: {profit:,.0f} | Days: {days_passed} | Asset: {Assets_Price:,.0f}"
            )

    window.resultBox.append(f"\nTotal Profit (Toman): {Total_profit:,.0f}")


def load_ui(ui_path):
    f = QFile(ui_path)
    if not f.open(QFile.ReadOnly):
        raise FileNotFoundError(f"Cannot open UI file: {ui_path}")

    loader = QUiLoader()
    w = loader.load(f)
    f.close()
    return w


def main():
    global window

    app = QApplication([])

    ui_path = os.path.join(os.path.dirname(__file__), "UI.ui")
    window = load_ui(ui_path)

    # ===== Connect Button (NEW objectName) =====
    if not hasattr(window, "calcBtn"):
        QMessageBox.critical(window, "Error", "calcBtn not found (objectName mismatch).")
        return

    if not hasattr(window, "resultBox"):
        QMessageBox.critical(window, "Error", "resultBox not found.")
        return

    window.calcBtn.clicked.connect(calculate_prog)

    window.setWindowTitle("Financial Assistant Project")
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
