from flask import Flask, request, render_template_string
import pyodbc

app = Flask(__name__)

# 🔌 SQL Server connection
def connect_to_db():
    server = '103.207.1.91'
    database = 'CSE9286'
    username = 'MZCET'
    password = 'MZCET@1234'
    driver = '{ODBC Driver 17 for SQL Server}'
    conn_str = f"""
        DRIVER={driver};
        SERVER={server};
        DATABASE={database};
        UID={username};
        PWD={password};
    """
    try:
        return pyodbc.connect(conn_str)
    except Exception as e:
        print("❌ DB Connection Error:", e)
        return None

# 🧾 HTML Template
template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Expense Tracker</title>
    <style>
        body { font-family: Arial; background: #f0f0f0; padding: 20px; }
        .container { background: #fff; padding: 20px; border-radius: 8px; max-width: 700px; margin: auto; box-shadow: 0 0 10px #ccc; }
        h2 { text-align: center; }
        input, select, textarea, button { width: 100%; padding: 10px; margin-top: 10px; }
        button { background: #28a745; color: white; font-weight: bold; border: none; }
        table { width: 100%; border-collapse: collapse; margin-top: 30px; }
        th, td { border: 1px solid #ccc; padding: 10px; text-align: center; }
        th { background-color: #28a745; color: white; }
        .success { color: green; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Add Expense</h2>
        {% if message %}
            <p class="success">{{ message }}</p>
        {% endif %}
        <form method="POST">
            <input type="number" name="amount" placeholder="Amount (₹)" required step="0.01">
            <select name="category" id="category-select" required onchange="toggleCustomCategory()">
                <option value="">Select Category</option>
                <option value="Food">Food</option>
                <option value="Travel">Travel</option>
                <option value="Shopping">Shopping</option>
                <option value="Bills">Bills</option>
                <option value="Other">Other</option>
            </select>
            <input type="text" name="custom_category" id="custom-category" placeholder="Enter custom category" style="display:none;">
            <input type="date" name="date" required>
            <textarea name="description" placeholder="Description" required></textarea>
            <button type="submit">Add Expense</button>
        </form>

        <h2>Expense History</h2>
        <table>
            <thead>
                <tr><th>ID</th><th>Date</th><th>Amount (₹)</th><th>Category</th><th>Description</th></tr>
            </thead>
            <tbody>
                {% for expense in expenses %}
                <tr>
                    <td>{{ expense.id }}</td>
                    <td>{{ expense.date }}</td>
                    <td>{{ expense.amount }}</td>
                    <td>{{ expense.category }}</td>
                    <td>{{ expense.description }}</td>
                </tr>
                {% endfor %}
                {% if not expenses %}
                <tr><td colspan="5">No expenses recorded.</td></tr>
                {% endif %}
            </tbody>
        </table>
    </div>

    <script>
    function toggleCustomCategory() {
        var select = document.getElementById("category-select");
        var customInput = document.getElementById("custom-category");
        if (select.value === "Other") {
            customInput.style.display = "block";
            customInput.required = true;
        } else {
            customInput.style.display = "none";
            customInput.required = false;
        }
    }
    </script>
</body>
</html>
'''

# 🚀 Main route
@app.route("/", methods=["GET", "POST"])
def expense_tracker():
    message = ""
    if request.method == "POST":
        try:
            amount = float(request.form["amount"])
            category = request.form["category"]
            if category == "Other":
                category = request.form.get("custom_category", "Other")
            date = request.form["date"]
            description = request.form["description"]

            conn = connect_to_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Expenses (amount, category, date, description)
                    VALUES (?, ?, ?, ?)
                """, (amount, category, date, description))
                conn.commit()
                conn.close()
                message = "✅ Expense added successfully!"
        except Exception as e:
            return f"<h3>Error inserting expense: {e}</h3>"

    # Fetch all expenses
    expenses = []
    try:
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, date, amount, category, description FROM Expenses ORDER BY date DESC")
            expenses = cursor.fetchall()
            conn.close()
    except Exception as e:
        return f"<h3>Error fetching expenses: {e}</h3>"

    return render_template_string(template, expenses=expenses, message=message)

if __name__ == "__main__":
    app.run(debug=True)
