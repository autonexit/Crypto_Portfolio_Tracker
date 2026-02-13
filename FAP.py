# ✅ Qt (PySide6) version of your CustomTkinter app
# هدف: کمترین تغییر در منطق (Coinmarket + CSV + calculate_prog) و فقط جایگزینی UI با Qt
# نیازمندی‌ها:
#   pip install pyside6 requests
#
# نکته:
# - این نسخه UI را با کد می‌سازد (مثل نسخه CustomTkinter). اگر بخوای "بدون کدنویسی UI"
#   داشته باشی، همون فایل main.ui + Qt Designer بهترینه.

import requests
import csv
import os
from datetime import date, datetime

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt

today = date.today()

# -----------------------------
# Coinmarket API
# -----------------------------
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
    except requests.exceptions.Timeout:
        print(f"❌ Timeout: اتصال به CoinMarket برقرار نشد برای {Crypto_Name}")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: سرور CoinMarket در دسترس نیست")
        return None
    except Exception as e:
        print(f"❌ خطا در دریافت قیمت {Crypto_Name}:", e)
        return None


# ✅ CHANGE: avoid crash if API fails
_btc = Coinmarket("BTC")
_ton = Coinmarket("TON")
BTC_Price = round(_btc, 5) if _btc is not None else 0.0  # ✅ CHANGE
ton_price = round(_ton, 5) if _ton is not None else 0.0  # ✅ CHANGE

USDT_Price_Now = 0.0


# -----------------------------
# Qt App
# -----------------------------
class CryptoPortfolioQt(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Financial Assistant Project")
        self.resize(1100, 700)

        # ----- Top bar
        self.title_lbl = QLabel("Financial Assistant")
        self.title_lbl.setAlignment(Qt.AlignCenter)
        self.title_lbl.setStyleSheet("font-size:24px; font-weight:700;")

        self.subtitle_lbl = QLabel(
            f"Live Prices: BTC={BTC_Price} | TON={ton_price}    (Date: {today})"
        )
        self.subtitle_lbl.setAlignment(Qt.AlignCenter)

        # ----- Form
        form_grid = QGridLayout()

        form_grid.addWidget(QLabel("USDT Toman Price"), 0, 0)
        self.usdt_toman_entry = QLineEdit()
        self.usdt_toman_entry.setPlaceholderText("مثلاً 60000")
        form_grid.addWidget(self.usdt_toman_entry, 0, 1)

        form_grid.addWidget(QLabel("Crypto Value Trade"), 0, 2)
        self.crypto_value_entry = QLineEdit()
        self.crypto_value_entry.setPlaceholderText("مثلاً 0.05")
        form_grid.addWidget(self.crypto_value_entry, 0, 3)

        form_grid.addWidget(QLabel("Crypto Symbol Trade"), 1, 0)
        self.crypto_symbol_entry = QLineEdit()
        self.crypto_symbol_entry.setPlaceholderText("BTC یا TON")
        form_grid.addWidget(self.crypto_symbol_entry, 1, 1)

        form_grid.addWidget(QLabel("USD Price of Trade"), 1, 2)
        self.crypto_usd_entry = QLineEdit()
        self.crypto_usd_entry.setPlaceholderText("مثلاً 43000")
        form_grid.addWidget(self.crypto_usd_entry, 1, 3)

        # ----- Buttons
        btn_row = QHBoxLayout()
        self.calc_btn = QPushButton("Calculate Profit")
        self.clear_btn = QPushButton("Clear Results")
        btn_row.addWidget(self.calc_btn)
        btn_row.addWidget(self.clear_btn)
        btn_row.addStretch(1)

        # ----- Results
        self.results_box = QTextEdit()
        self.results_box.setReadOnly(True)

        # ----- Layout root
        root = QVBoxLayout()
        root.addWidget(self.title_lbl)
        root.addWidget(self.subtitle_lbl)

        form_wrap = QWidget()
        form_wrap.setLayout(form_grid)
        root.addWidget(form_wrap)

        btn_wrap = QWidget()
        btn_wrap.setLayout(btn_row)
        root.addWidget(btn_wrap)

        root.addWidget(QLabel("Results"))
        root.addWidget(self.results_box, stretch=1)

        self.setLayout(root)

        # ----- Signals
        self.calc_btn.clicked.connect(self.calculate_prog)
        self.clear_btn.clicked.connect(self.clear_results)

        # ----- (اختیاری) استایل ساده دارک
        self.setStyleSheet("""
            QWidget { background-color: #111; color: #eee; font-size: 14px; }
            QLineEdit { background-color: #1c1c1c; border: 1px solid #333; padding: 8px; border-radius: 6px; }
            QPushButton { background-color: #1f6feb; border: none; padding: 10px 14px; border-radius: 8px; font-weight: 600; }
            QPushButton:hover { background-color: #2b7fff; }
            QTextEdit { background-color: #0f0f0f; border: 1px solid #333; padding: 10px; border-radius: 8px; }
        """)

    # -----------------------------
    # UI helpers (Qt)
    # -----------------------------
    def clear_results(self):
        self.results_box.clear()

    def append_result(self, text, color=None):
        # ✅ minimal replacement for CTkLabel list
        if color == "red":
            self.results_box.append(f"<span style='color:#ff5c5c;'>{text}</span>")
        elif color == "green":
            self.results_box.append(f"<span style='color:#3ddc84;'>{text}</span>")
        else:
            self.results_box.append(text)

    # -----------------------------
    # Main logic (almost unchanged)
    # -----------------------------
    def calculate_prog(self):
        global USDT_Price_Now  # ✅ same behavior

        self.clear_results()

        # ---- Read inputs (with guard)
        try:
            USDT_Price_Now = float(self.usdt_toman_entry.text())
        except Exception:
            self.append_result("❌ USDT Toman Price نامعتبر است.", "red")
            return

        # Optional trade row to append
        try:
            crypto_amount = float(self.crypto_value_entry.text() or 0)
        except Exception:
            self.append_result("❌ مقدار کریپتو نامعتبر است.", "red")
            return

        symbol_user = (self.crypto_symbol_entry.text() or "").strip().upper()
        try:
            usdt_buy_price = float(self.crypto_usd_entry.text() or 0)
        except Exception:
            self.append_result("❌ USD Price of Trade نامعتبر است.", "red")
            return

        crypto_user_price = None
        if crypto_amount > 0:
            if symbol_user == "BTC":
                crypto_user_price = BTC_Price
            elif symbol_user == "TON":
                crypto_user_price = ton_price
            else:
                self.append_result("❌ Symbol فقط BTC یا TON باشد.", "red")
                return

        # ---- Save to CSV (append)
        file_path = "prices.csv"
        file_exists = os.path.exists(file_path)

        with open(file_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if (not file_exists) or (os.path.getsize(file_path) == 0):
                writer.writerow(["user_value", "price", "USD Price", "symbol", "Date"])
            if crypto_amount > 0:
                writer.writerow([crypto_amount, crypto_user_price, usdt_buy_price, symbol_user, today])

        # ---- Profit calc (read whole file)
        def user_profit_from_row(row):
            """row is dict from DictReader"""
            try:
                user_value = float(row["user_value"])
                buy_crypto_price = float(row["price"])
                buy_usdt_price = float(row["USD Price"])
                sym = (row["symbol"] or "").strip().upper()
                d = row["Date"]
            except Exception:
                return None

            if sym == "BTC":
                target_crypto_price = BTC_Price
            elif sym == "TON":
                target_crypto_price = ton_price
            else:
                return None

            try:
                buy_date = datetime.strptime(d, "%Y-%m-%d").date()
            except Exception:
                return None

            duration_days = (today - buy_date).days

            buy_value_toman = user_value * buy_crypto_price * buy_usdt_price
            now_value_toman = user_value * target_crypto_price * USDT_Price_Now
            profit = now_value_toman - buy_value_toman

            return profit, sym, now_value_toman, duration_days

        total_profit = 0.0
        count_valid = 0

        try:
            with open("prices.csv", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader, start=2):  # line number in file
                    res = user_profit_from_row(row)
                    if res is None:
                        continue
                    profit, sym, asset_now, days_passed = res
                    total_profit += profit
                    count_valid += 1

                    # show each row (profit can be negative too)
                    color = "green" if profit > 0 else ("red" if profit < 0 else None)
                    self.append_result(
                        f"Row {idx}: {sym} | Profit: {profit:,.0f} | Days: {days_passed} | Asset Now: {asset_now:,.0f}",
                        color=color
                    )
        except FileNotFoundError:
            self.append_result("❌ فایل prices.csv پیدا نشد.", "red")
            return

        self.append_result("-" * 80)
        self.append_result(f"Trades counted: {count_valid}")
        self.append_result(
            f"Total Profit (Toman): {total_profit:,.0f}",
            "green" if total_profit >= 0 else "red"
        )


def main():
    app = QApplication([])
    win = CryptoPortfolioQt()
    win.show()
    app.exec()


if __name__ == "__main__":
    main()
