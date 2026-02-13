import requests
import csv
import os
from datetime import date
from datetime import datetime
from tkinter import *



today = date.today()

#Coinmarket API
def Coinmarket(Crypto_Name):
    API_KEY_coinmarket = "07af61ff-8f34-47ea-8f5e-94f161861357"

    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    params = {
        "symbol": Crypto_Name,
        "convert": "USD"
    }

    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": API_KEY_coinmarket
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    API_Crypto_Pirce = data["data"][Crypto_Name]["quote"]["USD"]["price"]
    return API_Crypto_Pirce

BTC_Price = Coinmarket('BTC')
ton_price = Coinmarket('TON')


    # API ninjas
   # API_KEY = "fa5lmXMz7bB3bdmyBLGD2Q==RFGHMbZxSnyKsNmf"

  #  url = "https://api.api-ninjas.com/v1/cryptoprice"
 #   params = {
  #      "symbol": "BTCUSD"
   # }

  ##  headers = {
   #     "X-Api-Key": API_KEY
 #   }

  #  BTC = requests.get(url, headers=headers, params=params)

# BTC Price and others things
#BTCC = BTC.json()
#symbol_BTC = BTCC["symbol"]
#Price_BTC = BTCC["price"]



# Price of USDT in Tomman

#USDT_Pirce_Now = float(input("Enter USDT Price in Tomman: "))

# User Data for each trade



USDT_Price_Now = 0.0
Crypto_User = 0
Symbol_User = None
USDT_User = 0.0

def calculate_prog():
    USDT_Price_Now = float(USDT_Toman.get())
    Crypto_User = float(Crypto_User_Value_GUI.get())
    if Crypto_User > 0:
        Symbol_User = str(Crypto_User_Symbol_GUI.get())
        USDT_User = float(Crypto_User_USD_GUI.get())
        if Symbol_User == "BTC":
            Crypto_User_Price = BTC_Price
        if Symbol_User == "TON":
            Crypto_User_Price = ton_price

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


    def user_profit(row_number_in_file,):
        profit = 0
        with open("prices.csv", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            User_Value_Get = None
            User_Price_Get = None
            user_usdt_price = None
            user_symbol_Get = None
            user_date_Get = None
            profit = 0.0
            for index, row in enumerate(reader, start=2):  # چون ردیف داده‌ها از خط 2 فایل شروع میشن
                if index == row_number_in_file:
                    User_Value_Get = row["user_value"]
                    User_Price_Get = row["price"]
                    user_usdt_price = row["USD Price"]
                    user_symbol_Get = row["symbol"]
                    user_date_Get = row["Date"]
                    break

            if not User_Value_Get or not User_Price_Get:
                return 0.0, None, None, None            # این ردیف رو بی‌خیال شو
            else:
                User_Buy_Price = float(User_Value_Get) * float(User_Price_Get) * float(user_usdt_price)
                if user_symbol_Get == "BTC":
                    Crypto_Price_Target = BTC_Price
                if user_symbol_Get == "TON":
                    Crypto_Price_Target = ton_price

                Price_Now = float(User_Value_Get) * float(Crypto_Price_Target) * float(USDT_Price_Now)

                user_date_Get_Nformat = datetime.strptime(user_date_Get, "%Y-%m-%d").date()
                duration = today - user_date_Get_Nformat

                profit = (Price_Now - User_Buy_Price)

                return profit, user_symbol_Get,Price_Now,duration.days




    Total_profit = 0.0
    for i in range(1,100):
        profit, symboll, Assets_Price, days_passed = user_profit(i)
        Total_profit = profit + Total_profit
        if profit > 0:
            Final = Label(
                app,
                text=f"Profit of Row N{i} for {symboll} is: {profit} for {days_passed} days, Total Asset: {Assets_Price} ",
                font=("Arial", 17),
            )
            Final.pack(pady=(1,10))
    Final_Totall= Label(app,
                        text=f"Total Profit at Tomman is:  {Total_profit}",
                        font=("Arial", 17),
                        fg="Green",
                        )
    Final_Totall.pack(pady=(1,50))



app = Tk()
app.title("Financial Assistant Project")
app.geometry("1000x600")
USDT_Toman_Text = Label(app,text="USDT Toman Price: ",fg="white",bg="black")
USDT_Toman_Text.pack()
USDT_Toman = Entry(app, width=20, fg="black", bg="white",justify=CENTER)
USDT_Toman.pack(pady=(1,10))
Crypto_User_Value_Text = Label(app,text="Enter Crypto Value Trade: ",fg="white",bg="black")
Crypto_User_Value_Text.pack()
Crypto_User_Value_GUI= Entry(app, width=20, fg="black", bg="white",justify=CENTER)
Crypto_User_Value_GUI.pack(pady=(1,10))

Crypto_User_Symbol_Text = Label(app,text="Enter Crypto Symbol Trade: ",fg="white",bg="black")
Crypto_User_Symbol_Text.pack()
Crypto_User_Symbol_GUI= Entry(app, width=20, fg="black", bg="white",justify=CENTER)
Crypto_User_Symbol_GUI.pack(pady=(1,10))

Crypto_User_USD_Text = Label(app,text="Enter USD Price of Trade: ",fg="white",bg="black")
Crypto_User_USD_Text.pack()
Crypto_User_USD_GUI= Entry(app, width=20, fg="black", bg="white",justify=CENTER)
Crypto_User_USD_GUI.pack(pady=(1,20))

btn_Calculate = Button(app, bg='green', fg='white', text="Calculate Profit", command=calculate_prog)
btn_Calculate.pack()





app.mainloop()
