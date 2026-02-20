import requests
from datetime import date
import sys
import os
import csv
from datetime import date
from datetime import datetime

from PySide6.QtWidgets import QApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QTimer  # <-- اضافه شد

today = date.today()

class Main:
    def __init__(self):
        loader = QUiLoader()
        ui_file = QFile("mainwindow.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file)
        ui_file.close()

        self.ui.calcBtn.clicked.connect(self.on_run)
        self.ui.resultBox.setText("")

        # اجرای خودکار بعد از بالا آمدن پنجره (تغییر کم ولی مهم)
        QTimer.singleShot(0, self.beginning)
        # <-- اضافه شد

    def Coinmarket(self, Crypto_Name):  # <-- self اضافه شد

        API_KEY_coinmarket = self.api_txt

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

    def credits_left(self):
        url = "https://pro-api.coinmarketcap.com/v1/key/info"
        headers = {"X-CMC_PRO_API_KEY": self.api_txt}

        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        return r.json()["data"]["usage"]["current_month"]["credits_left"]

    def beginning(self):

        with open("api.txt", encoding="utf-8") as f:
            self.api_txt = f.readline()

        try:
            self.ui.api_credit.setText(f"Your API credits left: {self.credits_left()}")
            self.btc_price = round(self.Coinmarket("BTC"),4)
            self.ton_price = round(self.Coinmarket("TON"),4)
            self.ui.resultBox.setText(f"BTC: {self.btc_price}\nTON: {self.ton_price}")
        except Exception as e:
            self.ui.resultBox.setText(f"Error: {e}")

    def on_run(self):

        USDT_Price_Now = float(self.ui.usdtEn.text())
        Crypto_User = float(self.ui.amountEn.text())

        if Crypto_User > 0:
            Symbol_User = self.ui.symbolEn.currentText()

            USDT_User = float(self.ui.usdBuyEn.text())
            if Symbol_User == "BTC":
                Crypto_User_Price = self.btc_price
            if Symbol_User == "TON":
                Crypto_User_Price = self.ton_price

        file_path = "prices.csv"
        # 1) اگر فایل وجود داشته باشه True میشه
        file_exists = os.path.exists(file_path)
        # 2) فایل رو در حالت append باز می‌کنیم
        with open(file_path, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            # 3) اگر فایل تازه ساخته شده یا خالیه، هدر رو بنویس
            if (not file_exists) or (os.path.getsize(file_path) == 0):
                writer.writerow(["user_value", "price", "USD Price", "symbol", "Date"])
            if Crypto_User > 0:
                # 4) ردیف داده رو اضافه کن
                writer.writerow([Crypto_User, Crypto_User_Price, USDT_User, Symbol_User, today])

        def user_profit(row_number_in_file):  # <-- self حذف شد
            self.profit = 0
            with open("prices.csv", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                User_Value_Get = None
                User_Price_Get = None
                user_usdt_price = None
                user_symbol_Get = None
                user_date_Get = None
                self.profit = 0.0

                for index, row in enumerate(reader, start=2):
                    if index == row_number_in_file:
                        User_Value_Get = row["user_value"]
                        User_Price_Get = row["price"]
                        user_usdt_price = row["USD Price"]
                        user_symbol_Get = row["symbol"]
                        user_date_Get = row["Date"]
                        break

                if not User_Value_Get or not User_Price_Get:
                    return 0.0, None, None, None
                else:
                    User_Buy_Price = float(User_Value_Get) * float(User_Price_Get) * float(user_usdt_price)

                    if user_symbol_Get == "BTC":
                        Crypto_Price_Target = self.btc_price  # <-- اصلاح شد
                    if user_symbol_Get == "TON":
                        Crypto_Price_Target = self.ton_price

                    Price_Now = float(User_Value_Get) * float(Crypto_Price_Target) * float(USDT_Price_Now)

                    user_date_Get_Nformat = datetime.strptime(user_date_Get, "%Y-%m-%d").date()
                    duration = today - user_date_Get_Nformat

                    self.profit = (Price_Now - User_Buy_Price)
                    return self.profit, user_symbol_Get, Price_Now, duration.days

        Total_profit = 0.0
        for i in range(1, 100):
            profit, symboll, Assets_Price, days_passed = user_profit(i)
            Total_profit = profit + Total_profit
            if symboll:
                text = f"Profit of Row N{i} for {symboll} is: {profit:,.2f} | for {days_passed} days, Total Asset: {Assets_Price:,.0f}"


                if profit > 0:
                    color = "green"
                else:
                    color = "red"

                self.ui.resultBox.append(f'<span style="color:{color};">{text}</span>')
        if Total_profit > 0:
            color = "green"
        else:
            color = "red"
        text = f"Total Profit is {Total_profit:,.0f}"
        self.ui.resultBox.append(f'<span style="color:{color};">{text}</span>')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    program = Main()
    program.ui.show()
    sys.exit(app.exec())
