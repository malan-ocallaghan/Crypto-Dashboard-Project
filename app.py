from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)
CORS(app)

@app.route('/api/getMessage', methods=['GET'])
def get_message():
    message = "Hello from the backend!"
    return jsonify({'message': message})

@app.route('/api/getBitcoinData', methods=['GET'])
def get_bitcoin_data():
    ticker_symbol = "BTC-USD"
    start_date = "2015-01-01"
    end_date = "2015-01-31"
    bitcoin_data = yf.download(ticker_symbol, start=start_date, end=end_date, interval="1d")
    
    # Reset the index and convert the DataFrame to a list of dictionaries
    bitcoin_data.reset_index(inplace=True)
    bitcoin_data = bitcoin_data.to_dict(orient='records')
    
    return jsonify(bitcoin_data)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
