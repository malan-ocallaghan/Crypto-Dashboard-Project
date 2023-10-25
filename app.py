from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
from yahooquery import Screener
from datetime import datetime
import pandas as pd

app = Flask(__name__)
CORS(app)

# Function to Get the List of Available Tickers and Send to Front End
@app.route('/api/getTickerOptions', methods=['GET'])
def get_ticker_options():

    # Add comments to this function...
    s = Screener()
    data = s.get_screeners('all_cryptocurrencies_us', count=250)
    dicts = data['all_cryptocurrencies_us']['quotes']
    symbols = [d['symbol'] for d in dicts]
    return jsonify({'tickerOptions': symbols})

# Function to Download Coin Data and Send to Front End
@app.route('/api/getCoinData', methods=['POST'])
def get_coin_data():

    # Storing the Variables from the Front End
    data = request.get_json()
    start_date = datetime.strptime(data['startDate'], "%Y/%m/%d")
    end_date = datetime.strptime(data['endDate'], "%Y/%m/%d")
    periodicity = data['periodicity']
    data_series = data['dataSeries']

    # Downloading the Data from Yahoo Finance
    coin_data = pd.DataFrame()
    for series in data_series:

        # Set the Current Ticker Name
        data_type = series['type']
        ticker = series['ticker']

        # Download the Data for the Ticker
        downloaded_data = yf.download(tickers = ticker, start = start_date, end = end_date, interval = periodicity)
        coin_data[ticker + ' (' + data_type + ')'] = downloaded_data[data_type]
        
    
    # Reset the index to add it as a column
    coin_data.reset_index(inplace=True)
    coin_data['Date'] = coin_data['Date'].dt.strftime('%Y-%m-%d')
    coin_data = coin_data.to_json(orient='records')
    return coin_data

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)


