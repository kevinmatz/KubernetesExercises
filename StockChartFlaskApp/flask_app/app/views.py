from app import app
# from app import FINANCIAL_DATA_SOURCE
from flask import render_template, request
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime
import os

# app = Flask(__name__)

FINANCIAL_DATA_SOURCE = os.getenv("DATAPROVIDER", "the universe")
print(f"Debug 1: FINANCIAL_DATA_SOURCE: {FINANCIAL_DATA_SOURCE}")

@app.route('/', methods=['GET'])
def index():
   print(f"Debug 2: FINANCIAL_DATA_SOURCE: {FINANCIAL_DATA_SOURCE}")
   return render_template('index.html', financial_data_source=FINANCIAL_DATA_SOURCE)

@app.route('/stock', methods=['POST'])
def stock():
   print(f"Debug 3: FINANCIAL_DATA_SOURCE: {FINANCIAL_DATA_SOURCE}")
   ticker = request.form['ticker']
   end_date = datetime.now()
   start_date = datetime(end_date.year - 1, end_date.month, end_date.day)
   data = yf.download(ticker, start=start_date, end=end_date)
   # data['Return'] = (1 + data['Close'].pct_change()).cumprod()
   plt.figure(figsize=(14, 7))
   plt.plot(data['Close'], 'r', label=ticker)
   plt.title(f'Stock Price Movement During the Last Year for Ticker Symbol {ticker}')
   plt.xlabel('Date')
   plt.ylabel('Stock Price')
   plt.legend()
   plt.grid(True)
   plt.savefig('app/static/stock_graph.png')  # Save the graph as a static file
   return render_template('stock.html', financial_data_source=FINANCIAL_DATA_SOURCE)
