# uthor: Clinton Daniel, University of South Florida
# Date: 4/4/2023
# Description: This is a Flask App that uses SQLite3 to
# execute (C)reate, (R)ead, (U)pdate, (D)elete operationsA

from flask import Flask
from flask import render_template,request, redirect, url_for, flash
from flask import request
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)

bcrypt = Bcrypt()
app.secret_key = 'itsmebilly004secretkey'

def create_connection():
    return sqlite3.connect(DATABASE)


DATABASE = 'database.db'
def create_table():
    conn = sqlite3.connect('database.db')
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Home Page route
@app.route("/")
def home():
    return render_template("home.html")

# Route to form used to add a new student to the database
@app.route("/enternew")
def enternew():
    return render_template("register.html")

# Route to add a new record (INSERT) student data to the database
@app.route('/addrec', methods=['POST'])
def addrec():
    create_table()  # Create the table if not exists
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        unhashed_password = request.form['password']
        phone = request.form['phone']


        password = bcrypt.generate_password_hash(unhashed_password).decode('utf-8')
        
        
        # Insert data into the registration table
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO registration (username, email, password, phone)
            VALUES (?, ?, ?, ?)
        ''', (username, email, password, phone))
        conn.commit()
        conn.close()

        return render_template('home.html', message='Registration successful!')
    else:
        return redirect(url_for('home'))
    
@app.route('/')
def index():
    # Get the success message from the query parameters
    message = request.args.get('message', '')
    return render_template('index.html', message=message)
        

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the form data
        username = request.form['username']
        password = request.form['password']


        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM registration WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        # Validate the user credentials
        if user and bcrypt.check_password_hash(user[0], password):
            return redirect(url_for('list'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

# Validate user credentials against the database
def validate_user(username, password):
    con = sqlite3.connect('database.db')
    cursor = con.cursor()

    # Check if the username and password match a record in the registration table
    cursor.execute('SELECT * FROM registration WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()

    con.close()

    return user is not None

# Route to SELECT all data from the database and display in a table      
@app.route('/list')
def list():
    # Connect to the SQLite3 datatabase and 
    # SELECT rowid and all Rows from the students table.
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM registration")

    rows = cur.fetchall()
    con.close()
    # Send the results of the SELECT to the list.html page
    return render_template("list.html",rows=rows)



# Route used to execute the UPDATE statement on a specific record in the database
@app.route("/editrec", methods=['POST','GET'])
def editrec():
    # Data will be available from POST submitted by the form
    if request.method == 'POST':
        try:
            # Use the hidden input value of id from the form to get the rowid
            rowid = request.form['rowid']
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            phone = request.form['phone']

            # UPDATE a specific record in the database based on the rowid
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("UPDATE registration SET username='"+username+"', email='"+email+"', password='"+password+"', phone='"+phone+"' WHERE rowid="+rowid)

                con.commit()
                msg = "Registration successful"
        except:
            con.rollback()
            msg = "Error in the Edit: UPDATE registration SET username="+username+", email="+email+", password="+password+", phone="+phone+" WHERE rowid="+rowid

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('result.html',msg=msg)

# Route used to DELETE a specific record in the database    
@app.route("/delete", methods=['POST','GET'])
def delete():
    if request.method == 'POST':
        try:
             # Use the hidden input value of id from the form to get the rowid
            rowid = request.form['id']
            # Connect to the database and DELETE a specific record based on rowid
            with sqlite3.connect('database.db') as con:
                    cur = con.cursor()
                    cur.execute("DELETE FROM registration WHERE rowid="+rowid)

                    con.commit()
                    msg = "Record successfully deleted from the database"
        except:
            con.rollback()
            msg = "Error in the DELETE"

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('result.html',msg=msg)
        
        
if __name__ == '__main__':
    app.run(debug=True)