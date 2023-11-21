# Importing the Required Packages for Managing our Backend
from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
from yahooquery import Screener
from datetime import datetime
import pandas as pd
from scipy import stats
from functools import reduce
from cryptocmd import CmcScraper
import os
import json
import threading
import mysql.connector

# Initialising our Flask Server
app = Flask(__name__)
data_processing_lock = threading.Lock()
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
CORS(app)


# MySQL Database Connection
def connect_to_database():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='crypto1234',
        database='cryptocanvasdb'
    )

# Login Endpoint
@app.route('/api/login', methods=['POST'])
def login_user():

    # Receive the Login Data From the Front End
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Connect to the Database
    connection = connect_to_database()
    cursor = connection.cursor()

    # Try Fetch User Details Based on the Provided Email
    try:
        cursor.execute('SELECT id, firstName, lastName, email, activeWidgets, userDefaults, collections, password FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()

        # If Matching Account Exists And Passwords Match Return User Data
        if user[-1] == password:

            # Compile the User Data
            userData = {
                'id': user[0],
                'firstName': user[1],
                'LastName': user[2],
                'email': user[3],
                'activeWidgets': user[4],
                'userDefaults': user[5],
                'collections': user[6],
                'password': user[7]
            }

            # Close theClose Connection and Return the User Data
            connection.close()
            return jsonify(userData)
        
        # If Matching Account Exists and Passwords Do Not Match Return Login Outcome as Incorrect Password
        else:

            # Close the Connection and Return Login Outcome
            connection.close()
            loginFailure = 'incorrect_password'
            return jsonify(loginFailure)



    # If No Matching Email Found, Return the Login Outcome as Unrecognized Email
    except:

        # Close the Connection and Return Login Outcome
        connection.close()
        loginFailure = 'no_email'
        return jsonify(loginFailure)
    
# Registration Endpoint
@app.route('/api/register', methods=['POST'])
def register_user():

    # Connect to the Data Base
    connection = connect_to_database()
    cursor = connection.cursor()

    # Get User Data From the Request
    data = request.get_json()
    firstName = data.get('firstName')
    lastName = data.get('lastName')
    email = data.get('email')
    password = data.get('password')
    activeWidgets = json.dumps([])
    userDefaults = json.dumps({'defaultWidgetHeaderColor': None, 'defaultWidgetBodyColor': None})

    collections_data = [
        {
            'name': 'Bitcoin Prices',
            'series': [
                {'name': 'BTC-O', 'case': 'Base', 'children': 'BTC-USD', 'childrenNames': ['BTC-USD'], 'method': 'Open', 'color': 'rgb(255,114,159)', 'display': True},
                {'name': 'BTC-C', 'case': 'Base', 'children': 'BTC-USD', 'childrenNames': ['BTC-USD'], 'method': 'Close', 'color': 'rgb(255,147,79)', 'display': True},
                {'name': 'BTC-H', 'case': 'Base', 'children': 'BTC-USD', 'childrenNames': ['BTC-USD'], 'method': 'Low', 'color': 'rgb(247,239,129)', 'display': True},
                {'name': 'BTC-L', 'case': 'Base', 'children': 'BTC-USD', 'childrenNames': ['BTC-USD'], 'method': 'High', 'color': 'rgb(104,176,171)', 'display': True},
            ],
            'favorite': True
        },
        {
            'name': 'Ethereum Prices',
            'series': [
                {'name': 'ETH-O', 'case': 'Base', 'children': 'ETH-USD', 'childrenNames': ['ETH-USD'], 'method': 'Open', 'color': 'rgb(255,114,159)', 'display': True},
                {'name': 'ETH-C', 'case': 'Base', 'children': 'ETH-USD', 'childrenNames': ['ETH-USD'], 'method': 'Close', 'color': 'rgb(255,147,79)', 'display': True},
                {'name': 'ETH-H', 'case': 'Base', 'children': 'ETH-USD', 'childrenNames': ['ETH-USD'], 'method': 'Low', 'color': 'rgb(247,239,129)', 'display': True},
                {'name': 'ETH-L', 'case': 'Base', 'children': 'ETH-USD', 'childrenNames': ['ETH-USD'], 'method': 'High', 'color': 'rgb(104,176,171)', 'display': True},
            ],
            'favorite': False
        },
                {
            'name': 'Binance Prices', 
            'series': [
                {'name': 'BNB-O', 'case': 'Base', 'children': 'BNB-USD', 'childrenNames': ['BNB-USD'], 'method': 'Open', 'color': 'rgb(255,114,159)', 'display': True},
                {'name': 'BNB-C', 'case': 'Base', 'children': 'BNB-USD', 'childrenNames': ['BNB-USD'], 'method': 'Close', 'color': 'rgb(255,147,79)', 'display': True},
                {'name': 'BNB-H', 'case': 'Base', 'children': 'BNB-USD', 'childrenNames': ['BNB-USD'], 'method': 'Low', 'color': 'rgb(247,239,129)', 'display': True},
                {'name': 'BNB-L', 'case': 'Base', 'children': 'BNB-USD', 'childrenNames': ['BNB-USD'], 'method': 'High', 'color': 'rgb(104,176,171)', 'display': True},
            ],
            'favorite': False
        },
                {
            'name': 'Cardano Prices', 
            'series': [
                {'name': 'ADA-O', 'case': 'Base', 'children': 'ADA-USD', 'childrenNames': ['ADA-USD'], 'method': 'Open', 'color': 'rgb(255,114,159)', 'display': True},
                {'name': 'ADA-C', 'case': 'Base', 'children': 'ADA-USD', 'childrenNames': ['ADA-USD'], 'method': 'Close', 'color': 'rgb(255,147,79)', 'display': True},
                {'name': 'ADA-H', 'case': 'Base', 'children': 'ADA-USD', 'childrenNames': ['ADA-USD'], 'method': 'Low', 'color': 'rgb(247,239,129)', 'display': True},
                {'name': 'ADA-L', 'case': 'Base', 'children': 'ADA-USD', 'childrenNames': ['ADA-USD'], 'method': 'High', 'color': 'rgb(104,176,171)', 'display': True},
            ],
            'favorite': False
        },
                {
            'name': 'Solana Prices', 
            'series': [
                {'name': 'SOL-O', 'case': 'Base', 'children': 'SOL-USD', 'childrenNames': ['SOL-USD'], 'method': 'Open', 'color': 'rgb(255,114,159)', 'display': True},
                {'name': 'SOL-C', 'case': 'Base', 'children': 'SOL-USD', 'childrenNames': ['SOL-USD'], 'method': 'Close', 'color': 'rgb(255,147,79)', 'display': True},
                {'name': 'SOL-H', 'case': 'Base', 'children': 'SOL-USD', 'childrenNames': ['SOL-USD'], 'method': 'Low', 'color': 'rgb(247,239,129)', 'display': True},
                {'name': 'SOL-L', 'case': 'Base', 'children': 'SOL-USD', 'childrenNames': ['SOL-USD'], 'method': 'High', 'color': 'rgb(104,176,171)', 'display': True},
            ],
            'favorite': False
        },
                {
            'name': 'FTT Prices', 
            'series': [
                {'name': 'FTT-O', 'case': 'Base', 'children': 'FTT-USD', 'childrenNames': ['FTT-USD'], 'method': 'Open', 'color': 'rgb(255,114,159)', 'display': True},
                {'name': 'FTT-C', 'case': 'Base', 'children': 'FTT-USD', 'childrenNames': ['FTT-USD'], 'method': 'Close', 'color': 'rgb(255,147,79)', 'display': True},
                {'name': 'FTT-H', 'case': 'Base', 'children': 'FTT-USD', 'childrenNames': ['FTT-USD'], 'method': 'Low', 'color': 'rgb(247,239,129)', 'display': True},
                {'name': 'FTT-L', 'case': 'Base', 'children': 'FTT-USD', 'childrenNames': ['FTT-USD'], 'method': 'High', 'color': 'rgb(104,176,171)', 'display': True},
            ],
            'favorite': False
        },
                        {
            'name': 'Top-5 Coins', 
            'series': [
                {'name': 'BTC-C', 'case': 'Base', 'children': 'BTC-USD', 'childrenNames': ['BTC-USD'], 'method': 'Close', 'color': '#E9DF00', 'display': True},
                {'name': 'ETH-C', 'case': 'Base', 'children': 'ETH-USD', 'childrenNames': ['ETH-USD'], 'method': 'Close', 'color': '#58A4B0', 'display': True},
                {'name': 'BNB-C', 'case': 'Base', 'children': 'BNB-USD', 'childrenNames': ['BNB-USD'], 'method': 'Close', 'color': '#03FCBA', 'display': True},
                {'name': 'ADA-C', 'case': 'Base', 'children': 'ADA-USD', 'childrenNames': ['ADA-USD'], 'method': 'Close', 'color': '#B744B8', 'display': True},
                {'name': 'FTT-C', 'case': 'Base', 'children': 'FTT-USD', 'childrenNames': ['FTT-USD'], 'method': 'Close', 'color': '#D64933', 'display': True},
            ],
            'favorite': False
        }
    ]

    collections = json.dumps(collections_data)

    # Collect Existing User Information if Any
    cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
    existing_user_id = cursor.fetchone()

    # Check if the User Already Exists
    if existing_user_id:
        registrationFailure = 'existing_email'
        return jsonify(registrationFailure)

    else:

        # Insert the new user into the database
        cursor.execute('INSERT INTO users (firstName, lastName, email, password, activeWidgets, userDefaults, collections) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                        (firstName, lastName, email, password, activeWidgets, userDefaults, collections))
        
        # Collect User Data After User Added to Database
        cursor.execute('SELECT id, firstName, lastName, email, activeWidgets, userDefaults, collections, password FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()

        # Compile the User Data
        userData = {
            'id': user[0],
            'firstName': user[1],
            'LastName': user[2],
            'email': user[3],
            'activeWidgets': user[4],
            'userDefaults': user[5],
            'collections': user[6],
            'password': user[7]
        }

        # Commit the Changes and Close the Connection
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify(userData)

# Your new update account settings endpoint
@app.route('/api/updateDashboardSettings/<int:user_id>', methods=['POST'])
def update_dashboard_settings(user_id):
    try:

        # Connect to the database
        connection = connect_to_database()
        cursor = connection.cursor()

        # Get user data from the request
        data = request.get_json()
        collections = json.dumps(data.get('collectionList'))
        userDefaults = json.dumps(data.get('userDefaults'))

        # Update the user details in the database
        cursor.execute('UPDATE users SET collections = %s, userDefaults = %s WHERE id = %s',
                    (collections, userDefaults, user_id))

        # Commit the changes and close the connection
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'success': True})

    except Exception as e:
        print('Error updating dashboard settings:', str(e))
        return jsonify({'error': 'Internal server error', 'success': False}), 500
    
# Your new update account settings endpoint
@app.route('/api/updateAccountSettings/<int:user_id>', methods=['POST'])
def update_account_settings(user_id):
    try:

        # Connect to the database
        connection = connect_to_database()
        cursor = connection.cursor()

        # Get user data from the request
        data = request.get_json()
        firstName = data.get('firstName')
        lastName = data.get('lastName')
        email = data.get('email')
        password = data.get('password')
        userDefaults = json.dumps(data.get('userDefaults'))

        # Update the user details in the database
        cursor.execute('UPDATE users SET firstName = %s, lastName = %s, email = %s, password = %s, userDefaults = %s WHERE id = %s',
                        (firstName, lastName, email, password, userDefaults, user_id))

        # Commit the changes and close the connection
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'success': True})

    except Exception as e:
        print('Error updating account settings:', str(e))
        return jsonify({'error': 'Internal server error', 'success': False}), 500

# Endpoint to update the dashboard layout
@app.route('/api/updateActiveWidgets/<int:user_id>', methods=['POST'])
def update_dashboard_layout(user_id):
    try:
        # Get the new dashboard layout from the request
        data = request.get_json()
        new_active_widgets = data.get('activeWidgets')

        # Connect to the database
        connection = connect_to_database()
        cursor = connection.cursor()

        # Update the dashboard layout for the specified user
        cursor.execute('UPDATE users SET activeWidgets = %s WHERE id = %s',
                       (json.dumps(new_active_widgets), user_id))

        # Commit the changes and close the connection
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/api/getRegisteredUsers', methods=['GET'])
def get_data():
    
    # Connect to the database
    connection = connect_to_database()
    cursor = connection.cursor()

    # Example query
    query = "SELECT * FROM users"
    cursor.execute(query)

    # Fetch all rows as a list of dictionaries
    data = [dict(zip(cursor.column_names, row)) for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    return jsonify(data)

@app.route('/api/deleteUser/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        # Connect to the database
        connection = connect_to_database()
        cursor = connection.cursor()

        # Delete the user from the database
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))

        # Commit the changes and close the connection
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'success': True}), 200
    except Exception as e:
        print('Error deleting user:', str(e))
        return jsonify({'error': 'Internal server error', 'success': False}), 500


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

    with data_processing_lock:
    
        # Define User Selection Mappings
        download_map = {"Daily": "1d", "Weekly": "1wk", "Monthly": "1mo", "Quarterly": "3mo", "Annual": "1y"}
        resample_map = {"Weekly": "W-MON", "Monthly": "MS", "Quarterly": "QS", "Annual": "AS-JAN"}
        method_map = {"Open": "Open", "Close": "Close", "Adjusted Close": "Adj Close", "Low": "Low", "High": "High", "Trading Volume": "Volume", "Market Capitalisation": "Market Cap"}
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
@app.route('/api/getHistoricalStatsData', methods=['POST'])
def get_historical_coin_statistics():
    
    # Define User Selection Mappings
    download_map = {"Daily": "1d", "Weekly": "1wk", "Monthly": "1mo", "Quarterly": "3mo", "Annual": "1y"}
    resample_map = {"Weekly": "W-MON", "Monthly": "MS", "Quarterly": "QS", "Annual": "AS-JAN"}
    method_map = {"Open": "Open", "Close": "Close", "Adjusted Close": "Adj Close", "Low": "Low", "High": "High", "Trading Volume": "Volume", "Market Capitalisation": "Market Cap"}
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
    statistics = data['Statistics']
    
    # Initial Download Frequency is the Periodicity
    download_freq = periodicity
    
    # Processed Data Series List
    processed_data = process_data_request(data_series, download_freq)
    
    coin_data = pd.DataFrame()
    for s in range(len(processed_data)):
        colname = data_series[s]["name"]
        coin_data[colname] = processed_data[s]
    
    stats_dict = {"Series": coin_data.columns}
    for statistic in statistics:
        if statistic == "Sum":
            stats_dict[statistic] = coin_data.sum()
        elif statistic == "Average":
            stats_dict[statistic] = coin_data.mean()
        elif statistic == "Mode":
            stats_dict[statistic] = coin_data.mode(axis=0).iloc[0]
        elif statistic == "Median":
            stats_dict[statistic] = coin_data.median()
        elif statistic == "Minimum":
            stats_dict[statistic] = coin_data.min()
        elif statistic == "Maximum":
            stats_dict[statistic] = coin_data.max()
        elif statistic == "Variance":
            stats_dict[statistic] = coin_data.var()
        elif statistic == "Standard Deviation":
            stats_dict[statistic] = coin_data.std()

            
            
    stats = pd.DataFrame(stats_dict)
    stats = stats.reset_index(drop=True)
    stats = stats.to_json(orient='records')
    return stats

# Function to Download Coin Data and Send to Front End
@app.route('/api/getHistoricalMatrixData', methods=['POST'])
def get_historical_coin_matrix():
    
    # Define User Selection Mappings
    download_map = {"Daily": "1d", "Weekly": "1wk", "Monthly": "1mo", "Quarterly": "3mo", "Annual": "1y"}
    resample_map = {"Weekly": "W-MON", "Monthly": "MS", "Quarterly": "QS", "Annual": "AS-JAN"}
    method_map = {"Open": "Open", "Close": "Close", "Adjusted Close": "Adj Close", "Low": "Low", "High": "High", "Trading Volume": "Volume", "Market Capitalisation": "Market Cap"}
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
    statistic = data['Statistics']
    
    # Initial Download Frequency is the Periodicity
    download_freq = periodicity
    
    # Processed Data Series List
    processed_data = process_data_request(data_series, download_freq)
    
    coin_data = pd.DataFrame()
    for s in range(len(processed_data)):
        colname = data_series[s]["name"]
        coin_data[colname] = processed_data[s]
    
    # Correlation Matrix
    if statistic == "Correlation":
        matrix = coin_data.corr()
    # Covariance Matrix
    elif statistic == "Covariance":
        matrix = coin_data.cov()
        
    # Convert to DataFrame
    matrix = pd.DataFrame(matrix)
    matrix = matrix.to_json(orient='split')
            
    return matrix

# Function to Download Coin Data and Send to Front End
@app.route('/api/getIntradayCoinData', methods=['POST'])
def get_intraday_coin_data():
    
    # Define User Selection Mappings
    download_map = {'1 Minute': '1m', '2 Minutes': '2m', '5 Minutes': '5m', '15 Minutes': '15m', '30 Minutes': '30m', '60 Minutes': '1h', '90 Minutes': '90m', 'Daily': '1d'}
    resample_map = {"Weekly": "W-MON", "Monthly": "MS", "Quarterly": "QS", "Annual": "AS-JAN"}
    method_map = {"Open": "Open", "Close": "Close", "Adjusted Close": "Adj Close", "Low": "Low", "High": "High", "Trading Volume": "Volume", "Market Capitalisation": "Market Cap"}
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
    coin_data['Datetime'] = coin_data['Datetime'].dt.strftime('%Y-%m-%d %H:%M')
    coin_data = coin_data.to_json(orient='records')
    return coin_data

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)


