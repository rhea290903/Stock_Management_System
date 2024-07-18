from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import random
import os
from decimal import Decimal
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# MySQL Connection
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Rs@290903',
    database='stock_market'
)
# SQL Trigger for User Signup
'''trigger_sql = """
DELIMITER //
CREATE TRIGGER before_insert_user
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
    SET NEW.user_id = FLOOR(RAND() * (999999 - 100000 + 1)) + 100000;
END;
//
DELIMITER ;
"""

# Execute the SQL Trigger
cursor = db.cursor()
cursor.execute(trigger_sql)
db.commit()
cursor.close()

# SQL Stored Procedure for Order Insertion
procedure_sql = """
DELIMITER //
CREATE PROCEDURE insert_order(IN p_order_id INT, IN p_user_id INT, IN p_stock_id INT, IN p_company_id INT, IN p_date DATETIME, IN p_price DECIMAL(10, 2), IN p_quantity INT, IN p_action VARCHAR(10), IN p_portfolio_name VARCHAR(255))
BEGIN
    DECLARE p_portfolio_id INT;
    DECLARE p_holding_id INT;

    -- Insert into orders table
    INSERT INTO orders (order_id, user_id, stock_id, company_id, date, price, quantity) VALUES (p_order_id, p_user_id, p_stock_id, p_company_id, p_date, p_price, p_quantity);

    -- Insert into user_portfolio table
    INSERT INTO user_portfolio (portfolio_id, company_id, user_id, portfolio_name) VALUES (FLOOR(RAND() * (999999 - 100000 + 1)) + 100000, p_company_id, p_user_id, p_portfolio_name);
    SET p_portfolio_id = LAST_INSERT_ID();

    -- Insert into portfolio_holdings table
    INSERT INTO portfolio_holdings (holding_id, portfolio_id, company_id, quantity, avg_buy_price) VALUES (FLOOR(RAND() * (999999 - 100000 + 1)) + 100000, p_portfolio_id, p_company_id, p_quantity, p_price);
    SET p_holding_id = LAST_INSERT_ID();

    -- Additional logic based on action (add/update)
    IF p_action = 'update' THEN
        -- Add logic for update if needed
    END IF;
END;
//
DELIMITER ;
"""

# Execute the SQL Stored Procedure
cursor = db.cursor()
cursor.execute(procedure_sql)
db.commit()
cursor.close()'''

# Function to check if a user exists in the database
def fetch_companies_data():
    cursor = db.cursor(dictionary=True)

    # Example query to fetch data from the "companies" table
    query = "SELECT * FROM companies"
    cursor.execute(query)
    data_companies = cursor.fetchall()

    cursor.close()
    return data_companies
def get_portfolio_holdings(user_id):
    cursor = db.cursor(dictionary=True)
    
    # Fetch portfolio_id associated with the user from user_portfolio
    cursor.execute("SELECT portfolio_id FROM user_portfolio WHERE user_id = %s", (user_id,))
    portfolio_ids = cursor.fetchall()

    # Fetch portfolio_holdings data based on portfolio_id
    portfolio_holdings_data = []
    for portfolio_id in portfolio_ids:
        cursor.execute("SELECT * FROM portfolio_holdings WHERE portfolio_id = %s", (portfolio_id['portfolio_id'],))
        holdings_for_portfolio = cursor.fetchall()
        portfolio_holdings_data.extend(holdings_for_portfolio)

    cursor.close()
    return portfolio_holdings_data

def check_user(username, password):
    cursor = db.cursor()
    query = "SELECT * FROM users WHERE username=%s AND password=%s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    cursor.close()
    return user
def get_stocks_data():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM stocks")
    data_stocks = cursor.fetchall()
    cursor.close()
    return data_stocks

def generate_unique_user_id():
    cursor = db.cursor()
    while True:
        # Generate a random user_id
        user_id = random.randint(100000, 999999)
        
        # Check if the user_id already exists
        query = "SELECT * FROM users WHERE user_id=%s"
        cursor.execute(query, (user_id,))
        existing_user = cursor.fetchone()
        
        # If user_id doesn't exist, break the loop
        if not existing_user:
            break
    
    cursor.close()
    return user_id
def get_user_data(user_id):
    cursor = db.cursor(dictionary=True)

    # Fetch user_portfolio data
    cursor.execute("SELECT * FROM user_portfolio WHERE user_id = %s", (user_id,))
    user_portfolio = cursor.fetchall()
    print("User Portfolio Data:", user_portfolio)  # Add this line for debugging

    # Fetch portfolio_holdings data based on portfolio_id
    portfolio_holdings_data = []
    for portfolio in user_portfolio:
        portfolio_id = portfolio['portfolio_id']
        cursor.execute("SELECT * FROM portfolio_holdings WHERE portfolio_id = %s", (portfolio_id,))
        holdings_for_portfolio = cursor.fetchall()
        portfolio_holdings_data.extend(holdings_for_portfolio)

    print("Portfolio Holdings Data:", portfolio_holdings_data)  # Add this line for debugging

    # Fetch orders data
    cursor.execute("SELECT * FROM orders WHERE user_id = %s", (user_id,))
    orders = cursor.fetchall()
    print("Orders Data:", orders)  # Add this line for debugging

    cursor.close()
    return user_portfolio, portfolio_holdings_data, orders


# Your routes for different pages
@app.route('/logout')
def logout():
    # Clear the session and redirect to the login page
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/update_orders')
def update_orders_page():
    # Fetch data or perform any necessary operations
    return render_template('update_order.html')
@app.route('/update_orders', methods=['POST'])
def update_orders():
    # Retrieve form data
    order_id = request.form.get('order_id')
    user_id = request.form.get('user_id')
    stock_id = request.form.get('stock_id')
    company_id = request.form.get('company_id')
    date = request.form.get('date')
    price = Decimal(request.form.get('price'))
    quantity = int(request.form.get('quantity'))
    action = request.form.get('action')
    portfolio_name= request.form.get('portfolio_name')

    

    if action == 'add':
        # Generate a random portfolio_id
        cursor = db.cursor()
        

        # Insert into the orders table
        query_orders = "INSERT INTO orders (order_id, user_id, stock_id, company_id, date, price, quantity) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query_orders, (order_id, user_id, stock_id, company_id, date, price, quantity))
        db.commit()
        cursor.close()
        
        cursor = db.cursor()
        portfolio_id = random.randint(100000, 999999)
        # Insert into the user_portfolio table
        query_user_portfolio = "INSERT INTO user_portfolio (portfolio_id, company_id, user_id, portfolio_name) VALUES (%s, %s, %s, %s)"
        cursor.execute(query_user_portfolio, (portfolio_id, company_id, user_id, portfolio_name))
        db.commit()
        cursor.close()
        # Generate a random holding_id
        holding_id = random.randint(100000, 999999)
        cursor = db.cursor()
        # Insert into the portfolio_holdings table
        query_portfolio_holdings = "INSERT INTO portfolio_holdings (holding_id, portfolio_id, company_id, quantity, avg_buy_price) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query_portfolio_holdings, (holding_id, portfolio_id, company_id, quantity, price))
        db.commit()
        cursor.close()
    elif action == 'update':
        # Update the orders table
        cursor = db.cursor()
        query_update_orders = "UPDATE orders SET user_id=%s, stock_id=%s, company_id=%s, date=%s, price=%s, quantity=%s WHERE order_id=%s"
        cursor.execute(query_update_orders, (user_id, stock_id, company_id, date, price, quantity, order_id))
        db.commit()
        cursor.close()
        # Fetch the portfolio_id associated with the user from user_portfolio
        cursor = db.cursor()
        query_portfolio_id = "SELECT portfolio_id FROM user_portfolio WHERE user_id = %s"
        cursor.execute(query_portfolio_id, (user_id,))
        result = cursor.fetchall()
        portfolio_id = result[0][0]
        print(portfolio_id)
        db.commit()
        cursor.close()


        
        
        # Update the user_portfolio table
        cursor = db.cursor()
        query_update_user_portfolio = "UPDATE user_portfolio SET company_id=%s, user_id=%s, portfolio_name=%s WHERE portfolio_id=%s"
        cursor.execute(query_update_user_portfolio, (company_id, user_id, portfolio_name, portfolio_id))
        db.commit()
        cursor.close()
        cursor=db.cursor()
        query_holding_id = "SELECT holding_id FROM portfolio_holdings WHERE portfolio_id = %s"
        cursor.execute(query_holding_id, (portfolio_id,))
        result = cursor.fetchall()
        holding_id = result[0][0]
        db.commit()
        cursor.close()
        # Update the portfolio_holdings table
        cursor = db.cursor()
        query_update_portfolio_holdings = "UPDATE portfolio_holdings SET portfolio_id=%s, company_id=%s, quantity=%s, avg_buy_price=%s WHERE holding_id=%s"
        cursor.execute(query_update_portfolio_holdings, (portfolio_id, company_id, quantity, price, holding_id))

        db.commit()
        cursor.close()
    
    
    # Redirect back to the main page after updating orders
    return render_template('update_order.html')

@app.route('/edit_stock_info', methods=['GET', 'POST'])
def edit_stock_info():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            # Handle adding a new stock
            stock_id = request.form.get('stock_id')
            company_id = request.form.get('company_id')
            volume = request.form.get('volume')
            low_price = request.form.get('low_price')
            high_price = request.form.get('high_price')
            closing_price = request.form.get('closing_price')
            opening_price = request.form.get('opening_price')
            date = request.form.get('date')

            # Add validation and error handling as needed

            # Perform the insert operation
            cursor = db.cursor()
            query = "INSERT INTO stocks (stock_id, company_id, volume, low_price, high_price, closing_price, opening_price, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (stock_id, company_id, volume, low_price, high_price, closing_price, opening_price, date))
            db.commit()
            cursor.close()

        elif action == 'update':
            # Handle updating an existing stock
            stock_id = request.form.get('stock_id')
            company_id = request.form.get('company_id')
            volume = request.form.get('volume')
            low_price = request.form.get('low_price')
            high_price = request.form.get('high_price')
            closing_price = request.form.get('closing_price')
            opening_price = request.form.get('opening_price')
            date = request.form.get('date')

            # Add validation and error handling as needed

            # Perform the update operation
            cursor = db.cursor()
            query = "UPDATE stocks SET company_id=%s, volume=%s, low_price=%s, high_price=%s, closing_price=%s, opening_price=%s, date=%s WHERE stock_id=%s"
            cursor.execute(query, (company_id, volume, low_price, high_price, closing_price, opening_price, date, stock_id))
            db.commit()
            cursor.close()

        elif action == 'delete':
            # Handle deleting a stock
            stock_id = request.form.get('stock_id')

            # Add validation and error handling as needed

            # Perform the delete operation
            cursor = db.cursor()
            query = "DELETE FROM stocks WHERE stock_id=%s"
            cursor.execute(query, (stock_id,))
            db.commit()
            cursor.close()

    # Add logic to fetch and display stock information
    return render_template('edit_stock_info.html')

@app.route('/edit_company_info', methods=['GET', 'POST'])
def edit_company_info():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            # Handle adding a new company
            company_id = request.form.get('company_id')
            company_name = request.form.get('company_name')
            sector = request.form.get('sector')
            industry = request.form.get('industry')

            # Add validation and error handling as needed

            # Perform the insert operation
            cursor = db.cursor()
            query = "INSERT INTO companies (company_id, name, sector, industry) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (company_id, company_name, sector, industry))
            db.commit()
            cursor.close()

        elif action == 'update':
            # Handle updating an existing company
            company_id = request.form.get('company_id')
            company_name = request.form.get('company_name')
            sector = request.form.get('sector')
            industry = request.form.get('industry')

            # Add validation and error handling as needed

            # Perform the update operation
            cursor = db.cursor()
            query = "UPDATE companies SET name=%s, sector=%s, industry=%s WHERE company_id=%s"
            cursor.execute(query, (company_name, sector, industry, company_id))
            db.commit()
            cursor.close()

        elif action == 'delete':
            # Handle deleting a company
            company_id = request.form.get('company_id')

            # Add validation and error handling as needed

            # Perform the delete operation
            cursor = db.cursor()
            query = "DELETE FROM companies WHERE company_id=%s"
            cursor.execute(query, (company_id,))
            db.commit()
            cursor.close()

    # Add logic to fetch and display company information
    return render_template('edit_company_info.html')
@app.route('/admin')
def admin_page():
    data_companies = fetch_companies_data()
    data_stocks = get_stocks_data()

    return render_template('admin.html', data_companies=data_companies,data_stocks=data_stocks)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html', message='')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username == "admin" and password == "admin@123":
        return redirect(url_for('admin_page'))
    user = check_user(username, password)

    if user:
        # If the login is successful, set the user_id in the session
        session['user_id'] = user[0]
        return redirect(url_for('main'))
    else:
        return render_template('login.html', message='Invalid credentials. Please try again.')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    user_id = generate_unique_user_id()

    cursor = db.cursor()
    query = "INSERT INTO users (user_id, username, email, password) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (user_id, username, email, password))
    db.commit()
    cursor.close()

    return redirect(url_for('login_page'))

@app.route('/main')
def main():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    user_id = session['user_id']
    user_details = get_user_data(user_id)

    # Fetch data for the logged-in user
    data_stocks = get_stocks_data()
    user_portfolio, portfolio_holdings, orders = get_user_data(user_id)

    return render_template('main.html', user_details=user_details, user_portfolio=user_portfolio, portfolio_holdings=portfolio_holdings, orders=orders,data_stocks=data_stocks)
    
    '''data_stocks = get_stocks_data()

    return render_template('main.html', data_stocks=data_stocks)'''

if __name__ == '__main__':
    app.run(debug=True)