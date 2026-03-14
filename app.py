from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import os
import json

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

DATA_FILE = "transactions.json"
BUDGET_FILE = "budget.json"


# ── Data helpers ──────────────────────────────────────────────────────────────

def load_transactions():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return []


def save_transaction(transaction_type, category, amount):
    transactions = load_transactions()
    transactions.append({
        "id": len(transactions) + 1,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": transaction_type,
        "category": category.strip().lower(),
        "amount": round(float(amount), 2)
    })
    with open(DATA_FILE, "w") as f:
        json.dump(transactions, f, indent=2)


def load_budget():
    if not os.path.exists(BUDGET_FILE):
        return 0
    with open(BUDGET_FILE, "r") as f:
        try:
            data = json.load(f)
            return float(data.get("amount", 0))
        except (json.JSONDecodeError, ValueError):
            return 0


def save_budget(amount):
    with open(BUDGET_FILE, "w") as f:
        json.dump({"amount": round(float(amount), 2)}, f)


def get_summary(transactions):
    total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
    total_expenses = sum(t["amount"] for t in transactions if t["type"] == "expense")
    balance = total_income - total_expenses
    budget = load_budget()

    income_by_cat = {}
    expense_by_cat = {}
    for t in transactions:
        if t["type"] == "income":
            income_by_cat[t["category"]] = income_by_cat.get(t["category"], 0) + t["amount"]
        else:
            expense_by_cat[t["category"]] = expense_by_cat.get(t["category"], 0) + t["amount"]

    budget_pct = round((total_expenses / budget * 100), 1) if budget > 0 else 0
    budget_remaining = round(budget - total_expenses, 2) if budget > 0 else 0

    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "balance": round(balance, 2),
        "budget": budget,
        "budget_pct": budget_pct,
        "budget_remaining": budget_remaining,
        "income_by_cat": dict(sorted(income_by_cat.items(), key=lambda x: x[1], reverse=True)),
        "expense_by_cat": dict(sorted(expense_by_cat.items(), key=lambda x: x[1], reverse=True)),
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    transactions = load_transactions()
    summary = get_summary(transactions)
    recent = sorted(transactions, key=lambda x: x["date"], reverse=True)[:10]
    return render_template("index.html", summary=summary, recent=recent)


@app.route("/add", methods=["GET", "POST"])
def add_transaction():
    if request.method == "POST":
        t_type = request.form.get("type")
        category = request.form.get("category", "").strip().replace(" ", "-")
        amount_str = request.form.get("amount", "")

        if not category:
            flash("Category is required.", "error")
            return redirect(url_for("add_transaction"))

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash("Please enter a valid amount greater than 0.", "error")
            return redirect(url_for("add_transaction"))

        save_transaction(t_type, category, amount)

        # Budget warning check
        if t_type == "expense":
            budget = load_budget()
            if budget > 0:
                total_expenses = sum(
                    t["amount"] for t in load_transactions() if t["type"] == "expense"
                )
                if total_expenses > budget:
                    flash(f"⚠️ You're £{total_expenses - budget:.2f} over your monthly budget!", "warning")
                elif total_expenses > budget * 0.9:
                    flash(f"⚠️ Heads up — only £{budget - total_expenses:.2f} left in your budget.", "warning")

        flash(f"{t_type.capitalize()} of £{amount:.2f} added successfully.", "success")
        return redirect(url_for("index"))

    return render_template("add.html")


@app.route("/transactions")
def transactions():
    all_tx = sorted(load_transactions(), key=lambda x: x["date"], reverse=True)
    return render_template("transactions.html", transactions=all_tx)


@app.route("/budget", methods=["GET", "POST"])
def budget():
    if request.method == "POST":
        try:
            amount = float(request.form.get("budget", 0))
            if amount < 0:
                raise ValueError
            save_budget(amount)
            flash(f"Monthly budget set to £{amount:,.2f}", "success")
        except ValueError:
            flash("Please enter a valid budget amount.", "error")
        return redirect(url_for("budget"))

    current_budget = load_budget()
    transactions = load_transactions()
    summary = get_summary(transactions)
    return render_template("budget.html", current_budget=current_budget, summary=summary)


@app.route("/api/chart-data")
def chart_data():
    transactions = load_transactions()
    # Monthly totals for last 6 months
    monthly = {}
    for t in transactions:
        month = t["date"][:7]  # YYYY-MM
        if month not in monthly:
            monthly[month] = {"income": 0, "expense": 0}
        monthly[month][t["type"]] = round(monthly[month][t["type"]] + t["amount"], 2)

    sorted_months = sorted(monthly.keys())[-6:]
    return jsonify({
        "labels": sorted_months,
        "income": [monthly[m]["income"] for m in sorted_months],
        "expenses": [monthly[m]["expense"] for m in sorted_months],
    })


@app.route("/delete/<int:transaction_id>", methods=["POST"])
def delete_transaction(transaction_id):
    transactions = load_transactions()
    transactions = [t for t in transactions if t["id"] != transaction_id]
    with open(DATA_FILE, "w") as f:
        json.dump(transactions, f, indent=2)
    flash("Transaction deleted.", "success")
    return redirect(url_for("transactions"))


@app.route("/clear", methods=["POST"])
def clear_data():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    if os.path.exists(BUDGET_FILE):
        os.remove(BUDGET_FILE)
    flash("All data cleared.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
