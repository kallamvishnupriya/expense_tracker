from flask import Flask, render_template, request, redirect
import mysql.connector
import json

app = Flask(__name__)

def get_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="vishnu@2888", 
        database="expense_db"
    )

# Dashboard
@app.route("/")
def index():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
    expenses = cursor.fetchall()

    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0]

    conn.close()

    return render_template("index.html", expenses=expenses, total=total)


# Add Expense
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        amount = request.form["amount"]
        category = request.form["category"]
        date = request.form["date"]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (amount, category, date) VALUES (%s, %s, %s)",
            (amount, category, date)
        )
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add.html")


# Delete Expense
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect("/")


# Edit Expense
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        amount = request.form["amount"]
        category = request.form["category"]
        date = request.form["date"]

        cursor.execute("""
            UPDATE expenses
            SET amount=%s, category=%s, date=%s
            WHERE id=%s
        """, (amount, category, date, id))

        conn.commit()
        conn.close()
        return redirect("/")

    cursor.execute("SELECT * FROM expenses WHERE id=%s", (id,))
    expense = cursor.fetchone()
    conn.close()

    return render_template("edit.html", expense=expense)


# Monthly Report
@app.route("/report")
def report():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DATE_FORMAT(date, '%Y-%m') AS month,
               SUM(amount) AS total
        FROM expenses
        GROUP BY month
        ORDER BY month DESC
    """)

    result = cursor.fetchall()
    conn.close()

    labels = [row[0] for row in result]
    values = [float(row[1]) for row in result]

    return render_template(
        "report.html",
        data=result,
        labels=labels,
        values=values
    )


if __name__ == "__main__":
    app.run(debug=True)
