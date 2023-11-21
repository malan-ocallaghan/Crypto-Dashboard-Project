## Installations

### Vue Installation
npm install -g vue
npm install -g @quasar/cli

Follow instructions for MySQL installation on your specific OS

### Vue Packages
npm install axios vue-router vue3-grid-layout 'chart.js/auto'

### Python Packages
pip install Flask Flask-Cors yfinance yahooquery pandas scipy cryptocmd

## Setup
### Setting up Backend
python3 -m venv env

### Setting Up SQL
# Access MySQL in the terminal:
mysql -u root -p
# Enter the root password when prompted.
# Create the database and table:
CREATE DATABASE cryptocanvasdb;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    firstName VARCHAR(255) NOT NULL,
    lastName VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    activeWidgets VARCHAR(255) NOT NULL,
    userDefaults VARCHAR(255) NOT NULL,
    collections VARCHAR(255) NOT NULL
);

## Launching the Web Application
In one terminal, run the Vue application:
npm run serve
In another terminal, run the Flask server:
python -m flask run
