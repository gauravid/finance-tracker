
from flask import Flask, render_template, request, redirect, session, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from collections import defaultdict
from datetime import datetime
import csv, os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Config
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Gauru@9422",
    database="finance_tracker"
)
cursor = db.cursor(dictionary=True)

# Upload Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Utility: Auto Categorization
def auto_categorize(description):
    description = description.lower()
    if any(word in description for word in ["uber", "fuel", "ola"]):
        return "Transport"
    elif any(word in description for word in ["zomato", "swiggy", "pizza", "restaurant"]):
        return "Food"
    elif any(word in description for word in ["electricity", "bill", "power"]):
        return "Utilities"
    elif any(word in description for word in ["rent", "lease"]):
        return "Rent"
    elif any(word in description for word in ["shopping", "amazon", "flipkart"]):
        return "Shopping"
    elif any(word in description for word in ["movie", "netflix", "hotstar"]):
        return "Entertainment"
    else:
        return "Other"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect('/dashboard')
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
        db.commit()
        return redirect('/login')
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    filter_option = request.args.get('filter', '30')
    if filter_option == '15':
        query = "SELECT * FROM transactions WHERE user_id = %s AND date >= CURDATE() - INTERVAL 15 DAY"
    elif filter_option == '7':
        query = "SELECT * FROM transactions WHERE user_id = %s AND date >= CURDATE() - INTERVAL 7 DAY"
    else:
        query = "SELECT * FROM transactions WHERE user_id = %s"

    cursor.execute(query, (session['user_id'],))
    transactions = cursor.fetchall()
    category_totals = defaultdict(float)
    monthly_totals = defaultdict(float)
    for txn in transactions:
        category_totals[txn['category']] += float(txn['amount'])
        month = txn['date'].strftime('%Y-%m') 
        monthly_totals[month] += float(txn['amount'])

    total_spent = sum(float(txn['amount']) for txn in transactions)

    return render_template('dashboard.html',
        transactions=transactions,
        chart_data=dict(category_totals),
        monthly_data=dict(monthly_totals),
        total_spent=total_spent,
        selected_filter=filter_option)

@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        date = request.form['date']
        description = request.form['description']
        cursor.execute("INSERT INTO transactions (user_id, amount, category, date, description) VALUES (%s, %s, %s, %s, %s)",
                       (session['user_id'], amount, category, date, description))
        db.commit()
        return redirect('/dashboard')
    return render_template('add_transaction.html')

@app.route('/set_budget', methods=['GET', 'POST'])
def set_budget():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        budget = request.form['budget']
        cursor.execute("REPLACE INTO budgets (user_id, amount) VALUES (%s, %s)", (session['user_id'], budget))
        db.commit()
        return redirect('/dashboard')

    cursor.execute("SELECT amount FROM budgets WHERE user_id = %s", (session['user_id'],))
    budget = cursor.fetchone()
    return render_template('set_budget.html', budget=budget['amount'] if budget else 0)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_transaction(id):
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        date = request.form['date']
        description = request.form['description']
        cursor.execute("""
            UPDATE transactions
            SET amount = %s, category = %s, date = %s, description = %s
            WHERE id = %s AND user_id = %s
        """, (amount, category, date, description, id, session['user_id']))
        db.commit()
        return redirect('/dashboard')

    cursor.execute("SELECT * FROM transactions WHERE id = %s AND user_id = %s", (id, session['user_id']))
    txn = cursor.fetchone()
    return render_template('edit_transaction.html', txn=txn)

@app.route('/delete/<int:id>')
def delete_transaction(id):
    if 'user_id' not in session:
        return redirect('/login')
    cursor.execute("DELETE FROM transactions WHERE id = %s AND user_id = %s", (id, session['user_id']))
    db.commit()
    return redirect('/dashboard')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            with open(filepath, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    amount = float(row.get('amount') or row.get('Amount') or 0)
                    description = row.get('description') or row.get('Description') or ''
                    category = auto_categorize(description)
                    date = row.get('date') or row.get('Date') or datetime.today().strftime('%Y-%m-%d')
                    cursor.execute("""
                        INSERT INTO transactions (user_id, amount, category, date, description)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (session['user_id'], amount, category, date, description))

                db.commit()

            return redirect('/dashboard')

    return render_template('upload.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
