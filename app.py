from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
from yahooquery import Screener
from datetime import datetime
import pandas as pd
from scipy import stats
from functools import reduce
from cryptocmd import CmcScraper

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
@app.route('/api/getHistoricalCoinData', methods=['POST'])
def get_historical_coin_data():
    
    # Define User Selection Mappings
    download_map = {"Daily": "1d", "Weekly": "1wk", "Monthly": "1mo", "Quarterly": "3mo", "Annual": "1y"}
    resample_map = {"Weekly": "W-MON", "Monthly": "MS", "Quarterly": "QS", "Annual": "AS-JAN"}
    method_map = {"Open": "Open", "Close": "Close", "Adjusted Close": "Adj Close", "Trading Volume": "Volume", "Market Capitalisation": "Market Cap"}
    # Recursive Function for Processing Data
    def process_data_request(request, download_freq):
        
        # Case of List Input
        if isinstance(request, list):
            result = [process_data_request(item, download_freq) for item in request]
        # Case of Dictionary Input
        elif isinstance(request, dict):
            
            # Determine the Case of the Dictionary
            case = request.get("case")
            
            # Case for Calculations Necessary
            if case == "Calculated":
                # If it's a Calculated Case, Process its Children
                result = process_data_request(request.get("children"), download_freq)
                # Get the Method of Calculation
                method = request.get("method")
                # Different Method of Calculations
                if method == "Change":
                    result = result[0]
                    result = result - result.shift(1)
                if method == "Percentage Change":
                    result = result[0]
                    result = (result / result.shift(1) - 1) * 100
                if method == "Sum":
                    result = sum(result)
                if method == "Difference":
                    result = result[0] - result[1]
                if method == "Product":
                    result = reduce(lambda x, y: x * y, result)
                if method == "Quotient":
                    result = result[0] / result[1]
            
            # Case for Aggregations Necessary
            elif case == 'Aggregated':
                # Determine the Aggregation Frequency
                agg_freq = request.get("from")
                # Set download_freq to agg_freq for this aggregation
                download_freq = agg_freq
                # If it's an Aggregated Case, Process its Children
                result = process_data_request(request.get("children"), download_freq)
                
                # Different Method of Aggregation
                method = request.get("method")
                if method == "Sum":
                    result = result[0]
                    result = result.resample(resample_map[periodicity]).sum()
                if method == "Average":
                    result = result[0]
                    result = result.resample(resample_map[periodicity]).mean()
                if method == "Mode":
                    result = result[0].resample(resample_map[periodicity])
                    result = result.apply(lambda x: stats.mode(x)[0])
                if method == "Median":
                    result = result[0]
                    result = result.resample(resample_map[periodicity]).median()
                if method == "Minimum":
                    result = result[0]
                    result = result.resample(resample_map[periodicity]).min()
                if method == "Maximum":
                    result = result[0]
                    result = result.resample(resample_map[periodicity]).max()
                if method == "Variance":
                    result = result[0]
                    result = result.resample(resample_map[periodicity]).var()
                if method == "Standard Deviation":
                    result = result[0]
                    result = result.resample(resample_map[periodicity]).std()
                if method == "Covariance":
                    result1 = pd.DataFrame(result[0])
                    result2 = pd.DataFrame(result[1])
                    result = pd.DataFrame.from_dict({col:pd.concat([result1[[col]],result2[[col]]],axis=1).groupby(pd.Grouper(freq=resample_map[periodicity])).apply(lambda x: x.cov().values[0,1]) for col in result1.columns})
                if method == "Correlation":
                    result1 = pd.DataFrame(result[0])
                    result2 = pd.DataFrame(result[1])
                    result = pd.DataFrame.from_dict({col:pd.concat([result1[[col]],result2[[col]]],axis=1).groupby(pd.Grouper(freq=resample_map[periodicity])).apply(lambda x: x.corr().values[0,1]) for col in result1.columns})
                
            # Case for Base Case
            elif case == "Base":

                children = request.get("children")
                method = request.get("method")

                if method == "Market Capitalisation":
                    # Use cryptocmd to download market capitalization data
                    coin_symbol = children.split("-")[0]
                    start_date_str = start_date.strftime("%d-%m-%Y")
                    end_date_str = end_date.strftime("%d-%m-%Y")
                    scraper = CmcScraper(coin_symbol, start_date_str, end_date_str)
                    result = scraper.get_dataframe()
                    result['Date'] = pd.to_datetime(result['Date'])
                    result.set_index('Date', inplace=True)
                    result = result[[method_map[method]]]

                else:
                    # If it's a Base Case, Perform Data Retrieval and Return the Value
                    downloaded_data = yf.download(tickers=children, start=start_date, end=end_date, interval=download_map[download_freq])
                    result = downloaded_data[method_map[method]]
                
        return result
    
    # Storing the Requests from Front-End
    data = request.get_json()
    start_date = datetime.strptime(data['startDate'], "%Y/%m/%d")
    end_date = datetime.strptime(data['endDate'], "%Y/%m/%d")
    periodicity = data['periodicity']
    data_series = data['dataSeries']
    
    # Initial Download Frequency is the Periodicity
    download_freq = periodicity
    
    # Processed Data Series List
    processed_data = process_data_request(data_series, download_freq)
    
    coin_data = pd.DataFrame()
    for s in range(len(processed_data)):
        colname = data_series[s]["name"]
        coin_data[colname] = processed_data[s]
    
    coin_data.reset_index(inplace = True)
    coin_data['Date'] = coin_data['Date'].dt.strftime('%Y-%m-%d')
    coin_data = coin_data.to_json(orient='records')
    return coin_data

# Function to Download Coin Data and Send to Front End
@app.route('/api/getIntradayCoinData', methods=['POST'])
def get_intraday_coin_data():
    
    # Define User Selection Mappings
    download_map = {'1 Minute': '1m', '2 Minutes': '2m', '5 Minutes': '5m', '15 Minutes': '15m', '30 Minutes': '30m', '60 Minutes': '1h', '90 Minutes': '90m', 'Daily': '1d'}
    resample_map = {"Weekly": "W-MON", "Monthly": "MS", "Quarterly": "QS", "Annual": "AS-JAN"}
    method_map = {"Open": "Open", "Close": "Close", "Adjusted Close": "Adj Close", "Trading Volume": "Volume"}
    # Recursive Function for Processing Data
    def process_data_request(request, download_freq):
        
        # Case of List Input
        if isinstance(request, list):
            result = [process_data_request(item, download_freq) for item in request]
        # Case of Dictionary Input
        elif isinstance(request, dict):
            
            # Determine the Case of the Dictionary
            case = request.get("case")
            
            # Case for Calculations Necessary
            if case == "Calculated":
                # If it's a Calculated Case, Process its Children
                result = process_data_request(request.get("children"), download_freq)
                # Get the Method of Calculation
                method = request.get("method")
                # Different Method of Calculations
                if method == "Change":
                    result = result[0]
                    result = result - result.shift(1)
                if method == "Percentage Change":
                    result = result[0]
                    result = (result / result.shift(1) - 1) * 100
                if method == "Sum":
                    result = sum(result)
                if method == "Difference":
                    result = result[0] - result[1]
                if method == "Product":
                    result = reduce(lambda x, y: x * y, result)
                if method == "Quotient":
                    result = result[0] / result[1]
            
            # Case for Aggregations Necessary
            elif case == 'Aggregated':
                # Determine the Aggregation Frequency
                agg_freq = request.get("from")
                # Set download_freq to agg_freq for this aggregation
                download_freq = agg_freq
                # If it's an Aggregated Case, Process its Children
                result = process_data_request(request.get("children"), download_freq)
                
                # Different Method of Aggregation
                method = request.get("method")
                if method == "Sum":
                    result = result[0]
                    result = result.resample(resample_map[periodicity]).sum()
                if method == "Average":
                    result = result[0]
                    result = result.resample(resample_map[periodicity]).mean()
                if method == "Mode":
                    result = result[0].resample(resample_map[periodicity])
                    result = result.apply(lambda x: stats.mode(x)[0])
                if method == "Median":
                    result = result[0]
                    result = result.resample(resample_map[periodicity]).median()
                if method == "Minimum":
                    result = result[0]
                    result = result.resample(resample_map[periodicity]).min()
                if method == "Maximum":
                    result = result[0]
                    result = result.resample(resample_map[periodicity]).max()
                if method == "Variance":
                    result = result[0]
                    result = result.resample(resample_map[periodicity]).var()
                if method == "Standard Deviation":
                    result = result[0]
                    result = result.resample(resample_map[periodicity]).std()
                if method == "Covariance":
                    result1 = pd.DataFrame(result[0])
                    result2 = pd.DataFrame(result[1])
                    result = pd.DataFrame.from_dict({col:pd.concat([result1[[col]],result2[[col]]],axis=1).groupby(pd.Grouper(freq=resample_map[periodicity])).apply(lambda x: x.cov().values[0,1]) for col in result1.columns})
                if method == "Correlation":
                    result1 = pd.DataFrame(result[0])
                    result2 = pd.DataFrame(result[1])
                    result = pd.DataFrame.from_dict({col:pd.concat([result1[[col]],result2[[col]]],axis=1).groupby(pd.Grouper(freq=resample_map[periodicity])).apply(lambda x: x.corr().values[0,1]) for col in result1.columns})
                
            # Case for Base Case
            elif case == "Base":

                children = request.get("children")
                method = request.get("method")

                if method == "Market Capitalisation":
                    # Use cryptocmd to download market capitalization data
                    coin_symbol = children.split("-")[0]
                    start_date_str = start_date.strftime("%d-%m-%Y")
                    end_date_str = end_date.strftime("%d-%m-%Y")
                    scraper = CmcScraper(coin_symbol, start_date_str, end_date_str)
                    result = scraper.get_dataframe()
                    result['Date'] = pd.to_datetime(result['Date'])
                    result.set_index('Date', inplace=True)
                    result = result[[method_map[method]]]

                else:
                    # If it's a Base Case, Perform Data Retrieval and Return the Value
                    downloaded_data = yf.download(tickers=children, start=start_date, end=end_date, interval=download_map[download_freq])
                    result = downloaded_data[method_map[method]]
                
        return result
    
    # Storing the Requests from Front-End
    data = request.get_json()
    start_date = datetime.strptime(data['startDate'], "%Y-%m-%d %H:%M")
    end_date = datetime.strptime(data['endDate'], "%Y-%m-%d %H:%M")
    periodicity = data['periodicity']
    data_series = data['dataSeries']
    
    # Initial Download Frequency is the Periodicity
    download_freq = periodicity
    
    # Processed Data Series List
    processed_data = process_data_request(data_series, download_freq)
    
    coin_data = pd.DataFrame()
    for s in range(len(processed_data)):
        colname = data_series[s]["name"]
        coin_data[colname] = processed_data[s]
    
    coin_data.reset_index(inplace = True)
    coin_data['Datetime'] = coin_data['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S%z')
    coin_data = coin_data.to_json(orient='records')
    return coin_data

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)


