import json
import requests
import time
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter, date2num
import pandas as pd
from datetime import datetime, timedelta
from pytz import timezone

key = "https://api.binance.com/api/v3/ticker/price?symbol="
history_key = "https://api.binance.com/api/v3/klines?symbol="

currencies = ["BTCUSDT", "DOGEUSDT", "LTCUSDT", "ETHUSDT", "TONUSDT","NOTUSDT","TRXUSDT"]

window = tk.Tk()
window.title("Цены на криптовалюты by nikoleta(Vadim Larionov)")

window.configure(background='#03A9F4')

frame = tk.Frame(window, bg='#333333')
frame.pack(padx=20, pady=20)

selected_currency = tk.StringVar()
selected_currency.set(currencies[0]) 

currency_menu = tk.OptionMenu(frame, selected_currency, *currencies)
currency_menu.config(font=("Trebuchet MS", 24), fg='#FFFFFF', bg='#333333')
currency_menu.grid(row=0, column=0)

time_intervals = ["1m", "5m", "1h", "1d"]
selected_interval = tk.StringVar()
selected_interval.set(time_intervals[0])
interval_menu = tk.OptionMenu(frame, selected_interval, *time_intervals)
interval_menu.config(font=("Trebuchet MS", 24), fg='#FFFFFF', bg='#333333')
interval_menu.grid(row=0, column=1)

fig, ax = plt.subplots(figsize=(8, 6))
chart_type = FigureCanvasTkAgg(fig, master=window)
chart_type.draw()
chart_type.get_tk_widget().pack(padx=20, pady=20)

labels = {}
previous_prices = {}
for i, currency in enumerate(currencies):
    label = tk.Label(frame, text=f"{currency} цена: ", font=("Trebuchet MS", 24), fg='#FFFFFF', bg='#333333')
    label.grid(row=i+1, column=0)
    labels[currency] = label
    previous_prices[currency] = None

def update_prices():
    currency = selected_currency.get()
    interval = selected_interval.get()  

    try:
        url = key + currency
        data = requests.get(url)
        data = data.json()
        price = float(data['price'])
        label = labels[currency]
        if previous_prices[currency] is not None:
            if price > previous_prices[currency]:
                label.config(text=f"{currency} цена: {price}", fg='green')
            elif price < previous_prices[currency]:
                label.config(text=f"{currency} цена: {price}", fg='red')
            else:
                label.config(text=f"{currency} цена: {price}", fg='#FFFFFF')
        else:
            label.config(text=f"{currency} цена: {price}", fg='#FFFFFF')
        previous_prices[currency] = price

        url = history_key + currency + f"&interval={interval}&limit=100"
        data = requests.get(url)
        data = data.json()

        df = pd.DataFrame(data, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
        df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
        df['Close'] = df['Close'].astype(float)

        if interval == "1m":
            df = df
        elif interval == "5m":
            df['Open time'] = pd.to_datetime(df['Open time'], unit='ms').dt.floor('5Min')
        elif interval == "1h":
            df['Open time'] = pd.to_datetime(df['Open time'], unit='ms').dt.floor('1H')
        elif interval == "1d":
            df['Open time'] = pd.to_datetime(df['Open time'], unit='ms').dt.floor('1D')

        df['Open time'] = date2num(df['Open time'])

        moscow_tz = timezone('Europe/Moscow')
        df['Open time'] = df['Open time'].apply(lambda x: datetime.fromtimestamp(x, moscow_tz))

        ax.clear()
        ax.plot(df['Open time'], df['Close'], marker='o', linestyle='-')
        ax.set_title(f"{currency} Price")
        ax.set_xlabel("Time (Moscow Time)")
        ax.set_ylabel("Price")

        date_formatter = DateFormatter('%Y-%m-%d %H:%M')
        ax.xaxis.set_major_formatter(date_formatter)
        plt.xticks(rotation=45)

        ax.xaxis.set_major_locator(plt.MaxNLocator(10))

        chart_type.draw()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
    window.after(5000, update_prices)

update_prices()

window.geometry("1400x1080")
window.resizable(False, False)

window.mainloop()