from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/getMessage', methods=['GET'])
def get_message():
    message = "Hello from the backend!"
    return jsonify({'message': message})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
