
import pandas as pd
from functools import wraps
from flask import Flask, session
from flask import render_template,request, redirect, url_for, flash, jsonify, Response, make_response
import time
import pdfkit
from flask import request
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
import os
from docx import Document
import csv
from werkzeug.utils import secure_filename


app = Flask(__name__)

property_info = []
messages = {'profile': [], 'admin': []}

log_file = "message_log.txt"


def log_message(sender, message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a') as file:
        file.write(f"{timestamp} - {sender}: {message}\n")

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/send_message', methods=['POST', 'GET'])
def send_message():
    sender = request.form['sender']
    recipient = 'admin' if sender == 'profile' else 'profile'
    message = request.form['message']
    messages[recipient].append({'sender': sender, 'message': message})
    log_message(sender, message)
    return jsonify({'success': True})

@app.route('/send_message2', methods=['POST','GET'])
def send_message2():
    sender = request.form['sender']
    recipient = 'home' if sender == 'profile' else 'profile'
    message = request.form['message']
    messages[recipient].append({'sender': sender, 'message': message})
    log_message(sender, message)
    return jsonify({'success': True})

# Implement logout route
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))
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

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def fetch_listings():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM listings")
    listings = cur.fetchall()
    conn.close()
    return listings

def mark_as_taken(property_id):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("UPDATE listings SET availability = 'Taken' WHERE id = ?", (property_id,))
    conn.commit()
    conn.close()

@app.route('/search', methods=['POST'])
def search():
    search_query = request.form['search_query']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM listings WHERE location LIKE ? OR type LIKE ? OR availability LIKE ? OR amount LIKE ? OR contact LIKE ?", ('%'+search_query+'%', '%'+search_query+'%', '%'+search_query+'%', '%'+search_query+'%', '%'+search_query+'%'))
    listings = cursor.fetchall()
    conn.close()
    return render_template('admin.html', listings=listings)

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM listings WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/download', methods=['POST'])
def download():
    # Fetch listings from the database
    listings = fetch_listings()

    # Create a DataFrame from the listings data
    df = pd.DataFrame(listings, columns=['id','Location', 'Type', 'Availability', 'Amount', 'Contact','image_path'])

    # Create an Excel writer object
    with pd.ExcelWriter('property_info.xlsx', engine='xlsxwriter') as writer:
        # Write the DataFrame to the Excel file
        df.to_excel(writer, index=False)

    # Open the Excel file for reading
    with open('property_info.xlsx', 'rb') as excel_file:
        excel_data = excel_file.read()

    # Create a response with Excel data
    response = make_response(excel_data)
    response.headers['Content-Disposition'] = 'attachment; filename=property_info.xlsx'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    # Remove the temporary Excel file
    os.remove('property_info.xlsx')

    return response

# Home Page route
@app.route("/" , methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        location = request.form.get('location')
        listing_type = request.form.get('type')
        listings = get_listings(location, listing_type)
        return render_template('home.html', listings=listings)
    return render_template('home.html', listings=None)

@app.route("/enternew")
def enternew():
    return render_template("register.html")

@app.route("/admin")
def admin():
    return render_template("admin.html",messages=messages['admin'])

def get_listings(location=None, listing_type=None):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    query = "SELECT * FROM listings WHERE 1=1"
    params = []

    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")
    if listing_type:
        query += " AND type LIKE ?"
        params.append(f"%{listing_type}%")

    cursor.execute(query, params)
    listings = cursor.fetchall()
    conn.close()
    return listings


# Route to form used to add a new student to the database
@app.route("/profile")
def profile():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM listings")
    listings = cursor.fetchall()
    conn.close()

    return render_template("profile.html",messages=messages['profile'], listings=listings)

# Route to add a new record (INSERT) student data to the database
@app.route('/addrec', methods=['POST'])
def addrec():
    create_table()  # Create the table if not exists
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        unhashed_password = request.form['password']
        phone = request.form['phone']

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM registration WHERE username = ? OR email = ?', (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username or email already exists!', 'error')
            conn.close()
            return redirect(url_for('login'))



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

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    else:
        return redirect(url_for('home'))
    
# @app.route('/')
# def index():
#     # Get the success message from the query parameters
#     message = request.args.get('message', '')
#     return render_template('index.html', message=message)
        

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
            
            return redirect(url_for('profile'))
             
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

        
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check if the file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            type TEXT,
            availability TEXT,
            amount INTEGER,
            contact INTEGER,
            image_path TEXT
        )
    ''')

    conn.commit()
    conn.close()
@app.route('/')
def index():
    init_db()
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM properties')
    properties = cursor.fetchall()

    conn.close()
    return render_template('properties.html', properties=properties)

# Route for uploading properties
@app.route('/upload', methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        location = request.form['location']
        prop_type = request.form['type']

        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        # If the user does not select a file, the browser submits an empty part without a filename
        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # Save the file to the uploads folder
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Insert data into the database
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO properties (location, type, image_path)
                VALUES (?, ?, ?)
            ''', (location, prop_type, file_path))
            conn.commit()
            conn.close()

            return redirect(url_for('properties'))

    return render_template('upload.html')

@app.route('/upload2', methods=['GET','POST'])
def upload2():
    if request.method == 'POST':
        location = request.form['location']
        prop_type = request.form['type']
        availability = request.form['availability']
        amount = request.form['amount']
        contact = request.form['contact']

        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        # If the user does not select a file, the browser submits an empty part without a filename
        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # Save the file to the uploads folder
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Insert data into the database
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO listings (location, type, availability, amount, contact, image_path)
                VALUES (?, ?, ?, ?, ?,?)
            ''', (location, prop_type, availability, amount, contact, file_path))
            conn.commit()
            conn.close()

            return redirect(url_for('listings'))

    return render_template('list.html')

# Route for displaying properties
@app.route('/properties')
def properties():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM properties')
    properties = c.fetchall()
    conn.close()

    return render_template('properties.html', properties=properties)

@app.route('/listings')
def listings():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM listings')
    listings = c.fetchall()
    conn.close()

    return render_template('listings.html', listings=listings)


def connect_db():
    conn = sqlite3.connect('database.db')
    return conn


@app.route('/results', methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        query = request.form['query']
        conn = connect_db()
        cursor = conn.cursor()
        # Execute SQL query to retrieve location and property_type
        cursor.execute("SELECT location FROM listings WHERE location LIKE ?", ('%' + query + '%',))
        results = cursor.fetchall()
        conn.close()
        return render_template('home.html', search_results=results)
    return 'Method Not Allowed', 405



if __name__ == '__main__':
    app.run(debug=True)