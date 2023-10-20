import pyodbc
from flask import Flask, request, render_template, redirect, url_for, session, url_for, flash
from flask_bcrypt import Bcrypt
from datetime import datetime, date
import re 
import sqlite3
import logging
app = Flask(__name__)
app.secret_key = 'your_secret_key' # Replace with your secret key
logging.basicConfig(filename="loggers1.log")
logger=logging.getLogger(__name__)
bcrypt = Bcrypt(app)
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + 'APINP-ELPT91232' + ';DATABASE=' + 'UPI_payment_system' + ';UID=' + 'sa' + ';PWD=' + 'tap2024')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('app.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

@app.route('/some_route', endpoint='some_route_endpoint')
def some_route():
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Users')
            data = cursor.fetchall()
            cursor.close()
            logger.info("Data retrieved successfully from the database.")
    except Exception as e:
        logger.error("Error retrieving data from the database.", exc_info=True)
        data = []

    return render_template('index.html', data=data)

@app.route('/')
def home():
    print('testing for home')
    return render_template('index.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            upi_id=username+"@ybl"
            password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Users (username, email, password,upi_id) VALUES (?, ?, ?, ?)", (username, email, password, upi_id))
            conn.commit()
            cursor.close()
            logger.info("User registered successfully: " + username)
            return redirect(url_for('login'))
        return render_template('register.html')
    except Exception as e:
        logger.error("Error while registering user: " + str(e))
        return "Error while registering user: " + str(e), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            cursor = conn.cursor()
            result = cursor.execute("SELECT * FROM Users WHERE email = ?", (email,))
            user = result.fetchone()
            cursor.close()
            if user and bcrypt.check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['username'] = user.username
                logger.info("User logged in successfully: " + user.username)
                return redirect(url_for('base'))
            else:
                logger.error("Login failed for user with email: " + email)
                flash('Login failed. Invalid credentials.', 'error')
        return render_template('login.html')
    except Exception as e:
        logger.error("Error while logging in user: " + str(e))
        return "Error while logging in user: " + str(e), 500

@app.route('/base')
def base():
    if 'user_id' in session:
        print(session['user_id'])
        return render_template('base.html')
    
    return redirect(url_for('base'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/notifications')
def notifications():
    if 'user_id' in session:
        transactions = get_recent_transactions_from_database(session['user_id'])
        return render_template('notifications.html', recent_transactions=transactions[0],recent_transactions1=transactions[1])
    return redirect(url_for('base'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' in session:
        # Fetch user information from the database
        cursor = conn.cursor()
        cursor.execute('SELECT username, email,upi_id FROM Users WHERE id = ?', (session['user_id'],))
        user_info = cursor.fetchone()
        # Fetch linked bank accounts for the user
        cursor.execute('SELECT id, bank_name, account_number FROM BankAccounts WHERE user_id = ?', (session['user_id'],))
        linked_accounts = cursor.fetchall()
        cursor.close()
        if request.method == 'POST':
            # Handle form submission for linking a new bank account
            account_number = request.form['account_number']
            bank_name = request.form['bank_name']
            upi_id=request.form['upi_id']
            # Perform necessary database operations to link the bank account to the user
            #link_upi(request.form['upi_id'])
            update_profile(session['user_id'],account_number,bank_name,upi_id)
            flash('Bank account linked successfully', 'success')
            return redirect(url_for('base'))
        return render_template('profile.html', user_info=user_info, linked_accounts=linked_accounts)
    return redirect(url_for('base'))


@app.route('/update_profile' ,methods=['POST'])
def update_profile():
    # Perform necessary database operations to link the bank account to the user
    name=request.form['username']
    email=request.form['email']
    cursor = conn.cursor()
    cursor.execute("Update users set username= ?, email=? where id= ?",(name,email,session['user_id']))
    conn.commit()
    cursor.close()
    return redirect(url_for('profile'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        username=session['username']
        # Fetch user's bank account balance from the database
        c = conn.cursor()
        c.execute('SELECT balance FROM BankAccounts WHERE user_id = ?', (user_id))
        balance = c.fetchall()
        c.close()
        # Fetch user's recent transactions from the database
        transactions = get_recent_transactions_from_database(user_id)
        return render_template('dashboard.html', account_balance=balance, recent_transactions=transactions) 

    return redirect(url_for('base'))

def get_recent_transactions_from_database(user_id):
    c = conn.cursor()
    c.execute('SELECT * FROM Transactions WHERE sender_id = ?', (user_id,))
    transactions = c.fetchall()
    c.execute('SELECT * FROM Transactions WHERE receiver_id = ?', (user_id,))
    transactions1=c.fetchall()
    c.close()
    return [transactions,transactions1]
    conn.close()

@app.route('/unlink_bank_account/<int:account_id>')
def unlink_bank_account(account_id):
    if 'user_id' in session:
        session['bank_account_to_unlink'] = account_id
        cursor = conn.cursor()
        cursor.execute('DELETE FROM BankAccounts WHERE id = ? and user_id = ?', (account_id,session['user_id']))
        conn.commit()
        cursor.close()
        flash('Bank account unlinked successfully', 'success')
    return redirect(url_for('profile'))


def is_valid_upi_id(upi_id):
# UPI ID should start with 'user@' followed by valid characters
    pattern = r'^user@[\w.-]+$'
    return re.match(pattern, upi_id)
# Example usage in the 'link_bank_account' route
@app.route('/link_bank_account', methods=['POST'])
def link_bank_account():
    if 'user_id' in session:
        bank_name = request.form['bank_name']
        account_number = request.form['account_number']
        cursor = conn.cursor()
        cursor.execute('INSERT INTO BankAccounts (user_id, bank_name, account_number) VALUES(?,?,?)',session['user_id'], bank_name, account_number)
        conn.commit()
        cursor.close()
        flash('Bank account linked successfully', 'success')
        return redirect(url_for('dashboard'))
    return redirect(url_for('base'))

@app.route('/link_upi', methods=['POST'])
def link_upi():
    if 'user_id' in session:
        bank_name = request.form['bank_name']
        upi_id = request.form['upi_id']
        if not is_valid_upi_id(upi_id):
            flash('Invalid UPI ID format. UPI ID should start with "user@"', 'error')
    return redirect(url_for('profile'))

@app.route('/transaction')
def transaction():
    if 'user_id' in session:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Transactions WHERE sender_id = ? OR receiver_id = ?',(session['user_id'], session['user_id']))
        transactions = cursor.fetchall()
        cursor.close()
        return render_template('transaction.html', transactions=transactions)
    return redirect(url_for('base'))

DAILY_SEND_LIMIT = 500 # Daily limit for sending money
DAILY_RECEIVE_LIMIT = 1000 # Daily limit for receiving money

def get_daily_transactions(user_id):
# Fetch user's daily transactions from the database
    today = date.today()
    cursor = conn.cursor()
    cursor.execute('SELECT amount FROM Transactions WHERE sender_id = ? AND date = ?', (user_id,
    today))
    transactions = cursor.fetchall()
    cursor.close()
    return sum(transaction.amount for transaction in transactions)

@app.route('/send_money', methods=['GET','POST'])
def send_money():
    try:
        if request.method=="POST":
            if 'user_id' in session:
                contact_id = request.form['contact_id']
                amount = request.form['amount']
                description = request.form['description']
                account_number = request.form['account_number']

                c = conn.cursor()
                c.execute('SELECT balance FROM BankAccounts WHERE user_id = ? and account_number=?', (session['user_id'], account_number))
                balance = c.fetchone()
                c.close()

                if int(amount) <= int(balance[0]):
                    cursor = conn.cursor()
                    cursor.execute('INSERT INTO Transactions (sender_id, receiver_id, amount, description) VALUES (?,?,?,?)',
                        (session['user_id'], contact_id, amount, description))
                    conn.commit()
                    cursor.close()

                    cursor1 = conn.cursor()
                    cursor1.execute("Update BankAccounts set balance= ? where user_id = ? and account_number = ?", (str(int(balance[0])-int(amount)), session['user_id'], account_number))
                    conn.commit()
                    cursor1.close()

                    cursor2 = conn.cursor()
                    cursor2.execute("Select balance from BankAccounts where user_id= ?", (contact_id,))
                    current_balance = int(cursor2.fetchall()[0][0])
                    cursor2.execute("Select account_number from BankAccounts where user_id= ?", (contact_id,))
                    current_account = str(cursor2.fetchall()[0][0])
                    cursor2.execute("Update BankAccounts set balance= ? where user_id = ? and account_number=?", (str(current_balance+int(amount)),contact_id,current_account))
                    conn.commit()
                    cursor2.close()
                    logger.info("Money sent successfully by user with user_id " + str(session["user_id"]))
                    flash('Money sent successfully', 'success')
                else:
                    logger.error("Insufficient funds while sending money by user with user_id " + str(session["user_id"]))
                    flash('Insufficient funds', 'error')
                return redirect(url_for('dashboard'))
        else:
            return render_template('send_money.html')
    except Exception as e:
        logger.error("Error while sending money by user with user_id " + str(session["user_id"]) + ". Error: " + str(e))
        return "Error while sending money: " + str(e), 500

if __name__ == '__main__':
    app.run(debug=True) 
