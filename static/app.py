from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired
import sqlite3



app = Flask(__name__)

# SQLite database configuration
DATABASE = 'database.db'
app.config['SECRET_KEY'] = 'thisismysecretkey'  # secret key for form security

def create_table():
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registration (
                id INTEGER PRIMARY KEY AUTO INCREMENT,
                username VARCHAR NOT NULL(12),
                phone INT NOT NULL(15),
                email VARCHAR(35) NOT NULL,
                password VARCHAR(120)
            )
        ''')
        connection.commit()

DATABASE = 'database.db'

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    submit = SubmitField('Register')

def create_table():
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                age INTEGER
            )
        ''')
        connection.commit()

@app.route("/addrec", methods = ['POST', 'GET'])
def addrec():
    # Data will be available from POST submitted by the form
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']

         
            # Connect to SQLite3 database and execute the INSERT
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO registration (name, addr, city, zip) VALUES (?,?,?,?)",(username, email, password, zip))

                con.commit()
                msg = "Record successfully added to database"
        except:
            con.rollback()
            msg = "Error in the INSERT"

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('home.html',msg=msg)

@app.route('/', methods=['GET', 'POST'])
def index():
    create_table()
    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        age = form.age.data

        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()
            cursor.execute('INSERT INTO users (username, age) VALUES (?, ?)', (username, age))
            connection.commit()

        return redirect(url_for('success'))

    return render_template('index.html', form=form)

@app.route('/success')
def success():
    return 'Registration successful!'

@app.route('/')
def home():
    create_table()
    return 'Flask App Connected to SQLite Database!'

    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/registration')
def registration():
    return render_template('registration.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/property')
def propertylist():
    return render_template('property.html')

if __name__ == '__main__':
    app.run(debug=True)
