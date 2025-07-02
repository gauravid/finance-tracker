# 💰 Spendly – Personal Finance Tracker

Spendly is a full-stack web application that helps users track their personal expenses, manage budgets, and visualize spending patterns over time. Users can add transactions manually or upload them in bulk via CSV, with automatic categorization and real-time summaries.

---

## 🚀 Features

- 🔐 **User Authentication** – Signup and login with hashed password storage (using Werkzeug).
- 📊 **Interactive Dashboard** – View expenses by category and time period (7/15/30 days).
- 📤 **CSV Upload Support** – Upload transaction records in bulk; auto-categorized based on description.
- ➕ **CRUD Operations** – Add, edit, or delete transactions and budgets.
- 📅 **Time-Based Filtering** – Toggle views for recent or all-time spending summaries.
- 🎨 **Data Visualization** – Category-wise expense breakdown using Chart.js.
- 📱 **Mobile-Friendly** – Responsive UI using Bootstrap and custom CSS.

---

## 🛠️ Tech Stack

- **Frontend**: HTML, CSS, JavaScript, Bootstrap, Chart.js, Jinja2 Templating
- **Backend**: Flask (Python)
- **Database**: MySQL
- **Authentication**: Werkzeug (Password hashing)
- **Data Handling**: CSV File Upload & Parsing

---

## 🧪 How to Run Locally

1. Clone the repo:
   ```bash
   git clone https://github.com/YOUR_USERNAME/finance-tracker.git
   cd finance-tracker
   ```
2. Create virtual environment (optional but recommended):

```bash
Copy
Edit
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4.Run the app:
```bash
python app.py
```
5.Visit: http://127.0.0.1:5000 in your browser.

## Note
1. Ensure a MySQL server is running and update credentials in app.py.

2. A finance_tracker database must exist with appropriate tables (users, transactions, budgets).



