import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

  # TODO Show the home page, portofolio of user
    user_id = session["user_id"]

    # Get user's stocks and shares
    stocks = db.execute(
        "SELECT symbol, price, SUM(shares) as total_shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING total_shares > 0", user_id)

    # Get user's cash balance
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]

 # Initialize variables for total values
    total = cash

    for stock in stocks:
        total += int(stock["price"]) * stock["total_shares"]

    return render_template("index.html", stocks=stocks, cash=cash, total=total, usd=usd)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    else:
        symbol = request.form.get("symbol")

        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("Shares must be a number")

        # If not a symbol
        if not symbol:
            return apology("Must give symbol.")

        # Show information Symbol and price
        stock = lookup(symbol.upper())

        # If symbol does not exist in stock
        if stock == None:
            return apology("Symbol does not exist.")

        if shares < 1:
            return apology("Share not allowed.")

        transaction_value = int(shares) * stock["price"]

        user_id = session["user_id"]
        user_cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_cash = user_cash_db[0]["cash"]
        if user_cash < transaction_value:
            return apology("Not enough money")

        uptd_cash = user_cash - transaction_value

        # Update database
        db.execute("UPDATE users SET cash = ? WHERE id = ?", uptd_cash, user_id)

        date = datetime.datetime.now()
        # Insert data(username, hashed password) int SQL database
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, date, type) VALUES(?, ?, ?, ?, ?, ?)",
                   user_id, stock["symbol"], shares, stock["price"], date, "buy")

        flash("Bought!")

        return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    transactions = db.execute(
        "SELECT type, symbol, price, shares, date FROM transactions wHERE user_id = ? ORDER BY date DESC", user_id)

    return render_template("history.html", transactions=transactions, usd=usd)


@app.route("/add_money", methods=["GET", "POST"])
@login_required
def add_money():
    """Add extra money to account"""
    if request.method == "GET":
        return render_template("add.html")
    else:
        new_money = request.form.get("new_money")

        if not new_money:
            return apology("Must give a number")
        elif new_money < 1:
            return apology("Must be a number greater than 0")
        else:
            new_money = int(new_money)

        user_id = session["user_id"]
        user_cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_cash = user_cash_db[0]["cash"]

        uptd_cash = user_cash + new_money

        # Update database
        db.execute("UPDATE users SET cash = ? WHERE id = ?", uptd_cash, user_id)

        flash("Money added!")

        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Show user his profile where he can make changes"""
    # Get username
    user_id = session["user_id"]
    username = db.execute("SELECT username FROM users where id = ?", user_id, username=username)

    if request.method == "GET":
        return render_template("profile.html", username=username)
    else:
        new_username = request.form.get("new-username")
        new_password = request.form.get("new-password")
        confirmation = request.form.get("confirmation")

        current_password = request.method.get("current-password")

        current_password_hash = db.execute("SELECT hash FROM users where id = ?", user_id)

        # Make sure passwords match
        if not check_password_hash(current_password_hash, current_password):
            return apology("Password does not match")

        # If change username
        elif new_username:

            # Check if username is taken
            if len(db.execute("SELECT username FROM users WHERE id = ?", new_username)):
                return apology("Username already exists")

            # Update username
            db.execute("UPDATE users SET username = ? WHERE id = ?", new_username, user_id)

            flash("Username changed")

        if new_password:

            # Check confirmation and new password are the same
            if new_password != confirmation:
                return apology("Passwords don't match")
            # Check old password and the new are not the same
            elif check_password_hash(current_password_hash, new_password):
                return apology("Password already in use")

            # Update password
            hash = generate_password_hash(new_password)
            db.execute("UPDATE users SET hash = ? WHERE id = ?", hash, user_id)

            # Display message of succes
            flash("Password changed")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")

    # Ask user for a stock (symbol) he wants a quote from
    else:
        symbol = request.form.get("symbol")

        # If not a symbol
        if not symbol:
            return apology("Must give symbol.")

        # Show information Symbol and price
        stock_quote = lookup(symbol.upper())

        # If symbol does not exist in stock
        if not stock_quote:
            return apology("Symbol does not exist")

        else:
            return render_template("quoted.html", stock=stock_quote)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user FIRST"""

    # TODO: Register new user and give apology if ther is no name, password or passwords don't match
    # User reached route vi POST

    # Forget any user ID
    session.clear()

    if request.method == "GET":
        return render_template("register.html")

    else:
        # Check username input
        username = request.form.get("username")
        if not username:
            return apology("Must give username.")

        # Check password input
        password = request.form.get("password")
        if not password:
            return apology("Must give password.")

        # Check confirmation
        confirmation = request.form.get("confirmation")
        if not confirmation:
            return apology("Must give confirmation.")

        # Check both passwords match
        if password != confirmation:
            return apology("Passwords do not match.")

        hash = generate_password_hash(password)

        # Make sure username does not exist
        try:
            # Insert data(username, hashed password) int SQL database
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)
        except:
            return apology("Username already exists.")

        return redirect("/")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]

    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))

        if shares <= 0:
            return apology("Shares must be greater than 0")
        item_price = lookup(symbol)["price"]

        price = int(shares) * item_price

        shares_owned = db.execute(
            "SELECT SUM(shares) as total_shares FROM transactions WHERE user_id = ? AND symbol = ?", user_id, symbol)[0]["total_shares"]

        if shares_owned < shares:
            return apology("Not enough shares")

        date = datetime.datetime.now()
        current_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
        db.execute("UPDATE users SET cash = ? WHERE id = ?", current_cash + price, user_id)
        db.execute("INSERT INTO transactions (user_id, shares, price, symbol, date, type) VALUES (?, ?, ?, ?, ?, ?)",
                   user_id, -shares, item_price, symbol, date, "sell")

        flash("Sold")

        return redirect("/")

    else:
        symbols = db.execute(
            "SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol", user_id)
        return render_template("sell.html", symbols=symbols)
