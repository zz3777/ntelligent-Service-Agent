import json
import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = "mock-crm-demo-key"

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"customers": [], "orders": []}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("username") == "admin" and request.form.get("password") == "demo123":
            session["user"] = "admin"
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="用户名或密码错误")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    data = load_data()
    return render_template("dashboard.html", customer_count=len(data["customers"]), order_count=len(data["orders"]))


@app.route("/customers")
def customers():
    if "user" not in session:
        return redirect(url_for("login"))
    data = load_data()
    return render_template("customers.html", customers=data["customers"])


@app.route("/customers/new", methods=["GET", "POST"])
def customer_new():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        data = load_data()
        customer = {
            "id": len(data["customers"]) + 1,
            "name": request.form["name"],
            "phone": request.form.get("phone", ""),
            "email": request.form.get("email", ""),
            "company": request.form.get("company", ""),
        }
        data["customers"].append(customer)
        save_data(data)
        return redirect(url_for("customers"))
    return render_template("customer_form.html")


@app.route("/orders")
def orders():
    if "user" not in session:
        return redirect(url_for("login"))
    data = load_data()
    return render_template("orders.html", orders=data["orders"])


@app.route("/orders/new", methods=["GET", "POST"])
def order_new():
    if "user" not in session:
        return redirect(url_for("login"))
    data = load_data()
    if request.method == "POST":
        order = {
            "id": len(data["orders"]) + 1,
            "customer_name": request.form["customer_name"],
            "product": request.form.get("product", ""),
            "amount": request.form.get("amount", "0"),
            "status": "新建",
        }
        data["orders"].append(order)
        save_data(data)
        return redirect(url_for("orders"))
    return render_template("order_form.html", customers=data["customers"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
