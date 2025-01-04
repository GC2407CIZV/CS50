import os
import sqlite3
from dotenv import load_dotenv
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, jsonify, session
from flask_session import Session
import socket
from werkzeug.security import check_password_hash, generate_password_hash
import bleach
import time
from datetime import datetime, timedelta

from helpers import apology, login_required, allowed_tags, allowed_attrs


# Access API key and SECRET key
load_dotenv()
API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config.update(
    SESSION_COOKIE_SECURE=True,    # Only send cookies over HTTPS
    SESSION_COOKIE_HTTPONLY=True,  # Prevent JavaScript from accessing cookies
    SESSION_COOKIE_SAMESITE='Lax',  # Mitigate CSRF attacks
    SESSION_PERMANENT=False,
    SESSION_TYPE="filesystem"
)
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///game.db")


# Utility function to sanitize input
def sanitize_input(input_data):
    return bleach.clean(input_data, tags=allowed_tags, attributes=allowed_attrs)


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers.update({
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Expires": 0,
        "Pragma": "no-cache"
    })
    return response


# @app.template_filter('format_time')
def format_time(seconds: int) -> str:
    if seconds is None:
        return "N/A"  # Handle cases where time_spent is missing or None

    seconds = int(seconds)  # Ensure seconds is an integer
    # Calculate days and remainder (86400 seconds in a day)
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)  # Calculate hours and remainder
    minutes, seconds = divmod(remainder, 60)    # Calculate minutes and seconds

    # If there are days, format as DD:HH:MM:SS, else format as HH:MM:SS
    if days > 0:
        return f'{days:02}:{hours:02}:{minutes:02}:{seconds:02}'  # Format as DD:HH:MM:SS
    else:
        return f'{hours:02}:{minutes:02}:{seconds:02}'  # Format as HH:MM:SS if no days


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()

    if request.method == "GET":
        return render_template("register.html")

    username = sanitize_input(request.form.get("username"))
    password = sanitize_input(request.form.get("password"))
    confirmation = sanitize_input(request.form.get("confirmation"))
    fingerprint = sanitize_input(request.form.get("fingerprint"))  # New field for fingerprint
    user_ip = request.remote_addr  # Get user IP address

    # Validate the form inputs
    if not username or not password:
        return apology("Must provide username and password.")
    if password != confirmation:
        return apology("Passwords don't match.")

    # Check for cookies to prevent multiple registrations
    if 'registered' in request.cookies:
        return apology("You have already registered.")

    # Get current time for registration
    registration_time = datetime.utcnow()

    with get_db_connection() as conn:
        # Check if IP address has registered in the last year
        existing_user_ip = conn.execute(
            "SELECT * FROM users WHERE ip = ? AND registration_time > ?",
            (user_ip, registration_time - timedelta(days=365))
        ).fetchall()
        if existing_user_ip:
            return apology("Multiple registrations from the same IP address are not allowed.")

        # Check if the fingerprint has been used to register
        existing_user_fp = conn.execute(
            "SELECT * FROM users WHERE fingerprint = ?",
            (fingerprint,)
        ).fetchall()
        if existing_user_fp:
            return apology("This device has already registered.")

        # Check if the username already exists
        existing_user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchall()
        if existing_user:
            return apology("Username already exists.")

        # Generate a password hash
        hash = generate_password_hash(password)

        # Insert new user data into the database
        try:
            conn.execute(
                "INSERT INTO users (username, hash, fingerprint, ip, registration_time) VALUES (?, ?, ?, ?, ?)",
                (username, hash, fingerprint, user_ip, registration_time)
            )
            conn.commit()  # Commit the changes
        except Exception as e:
            return apology(f"Registration failed: {str(e)}")

        # Set a cookie to prevent further registrations
        response = redirect("/login")
        # Calculate an expiration date 1 year from now
        expiration_date = datetime.utcnow() + timedelta(days=365*1)
        response.set_cookie('registered', 'true', expires=expiration_date)  # Cookie never expire

        # Flash success message and redirect to login
        flash("Registered successfully!")
        return response


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":
        username = sanitize_input(request.form.get("username"))
        password = sanitize_input(request.form.get("password"))

        if not username or not password:
            return apology("Must provide username and password", 403)

        user = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(user) != 1 or not check_password_hash(user[0]["hash"], password):
            # Increment failed attempts in session
            if "failed_attempts" not in session:
                session["failed_attempts"] = 0
            session["failed_attempts"] += 1

            # Apply rate limit if failed attempts exceed limit
            if session["failed_attempts"] > 3:
                return apology("Too many failed login attempts. Please try again later.", 429)

            flash("Invalid username and/or password", 403)
            return redirect("/login")

        # Reset failed attempts on successful login
        session.pop("failed_attempts", None)

        session["user_id"] = user[0]["id"]

        # Retrieve accumulated time from the database
        accumulated_time = db.execute(
            "SELECT time_spent FROM player_progress WHERE user_id = ?", user[0]["id"])
        session["accumulated_time"] = accumulated_time[0]["time_spent"] if accumulated_time else 0.0

        # Start tracking session time
        session["start_time"] = time.time()

        return redirect("/")  # Main page

    return render_template("login.html")


@app.route("/update_time", methods=["POST"])
@login_required
def update_time():
    """Update player's time in the database"""
    total_time_spent = request.json.get("total_time_spent")
    db.execute("UPDATE player_progress SET time_spent = ? WHERE user_id = ?",
               total_time_spent, session["user_id"])
    return jsonify(success=True)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Show user profile and allow changes"""
    user_id = session["user_id"]

    if request.method == "GET":
        return render_template("profile.html")

    new_username = sanitize_input(request.form.get("new-username"))
    new_password = sanitize_input(request.form.get("new-password"))
    confirmation = sanitize_input(request.form.get("confirmation"))

    if new_username:
        try:
            db.execute("UPDATE users SET username = ? WHERE id = ?", new_username, user_id)
            flash("Username changed successfully!")
        except sqlite3.IntegrityError:
            return apology("Username already exists.")
        except Exception as e:
            return apology("Error changing username.", e)

    if new_password:
        if new_password != confirmation:
            return apology("Passwords don't match.")
        hash_password = generate_password_hash(new_password)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", hash_password, user_id)
        flash("Password changed successfully!")

    return redirect("/profile")


@app.route("/logout")
def logout():
    """Log user out and save session time"""
    # Calculate the total time spent in the session
    current_time_spent = time.time() - session.get("start_time", 0)
    accumulated_time = session.get("accumulated_time", 0)

    # Update the accumulated time
    total_time_spent = accumulated_time + current_time_spent

    # Save the total time to the database
    db.execute("UPDATE player_progress SET time_spent = ? WHERE user_id = ?",
               total_time_spent, session["user_id"])

    # Clear the session
    session.clear()
    return redirect("/login")


@app.route("/")
@login_required
def index():
    user_id = session.get("user_id")  # Using get to avoid KeyError

    # Ensure user is logged in
    if user_id is None:
        return redirect('/login')

    # Get accumulated time from the session (default to 0 if not found)
    accumulated_time = session.get("accumulated_time", 0.0)

    # Ensure accumulated_time is a float
    accumulated_time = float(accumulated_time)

    # Check if 'start_time' is set in the session; if not, initialize it
    if "start_time" not in session:
        session["start_time"] = time.time()  # Set the start time if it doesn't exist

    # Calculate time spent in the current session
    current_time = time.time() - session["start_time"]

    # Calculate total time spent: accumulated time + time in the current session
    total_time_spent = accumulated_time + current_time

    # Fetch clues related to the user
    clue_ids = get_clue_ids(user_id)
    clues = db.execute(
        "SELECT * FROM player_progress WHERE user_id = ? ORDER BY timestamp DESC", user_id)

    # Calculate the number of clues found and total clues
    clues_found = len(clues)  # Number of clues found by the user
    total_clues = 22  # Total number of clues in the game

    # Optionally store total_time_spent back in session
    session["total_time_spent"] = total_time_spent

    return render_template(
        "index.html",
        clues=clues,
        clue_ids=clue_ids,
        total_time_spent=total_time_spent,
        clues_found=clues_found,
        total_clues=total_clues
    )

@app.route("/get_hint", methods=["POST"])
@login_required
def get_hint():
    """Return a hint for the next clue based on the user's progress and add 10 minutes to their total time."""
    user_id = session["user_id"]

    # Step 1: Retrieve the last clue_id from player_progress
    latest_progress = db.execute("SELECT clue_id, time_spent FROM player_progress WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1", user_id)

    # If no progress found, prompt the user to start at "About"
    if not latest_progress:
        flash("You should start by finding the clue on the About platform!")
        return redirect("/")  # Redirect to the main page or wherever appropriate

    last_clue_id = latest_progress[0]["clue_id"]
    accumulated_time = latest_progress[0]["time_spent"] or 0  # Set to 0 if None

    # Step 2: Find the next_clue_id from clues table based on last_clue_id
    next_clue = db.execute("SELECT next_clue_id FROM clues WHERE id = ?", last_clue_id)

    if not next_clue:
        return apology("No next clue found for this clue.", 404)

    next_clue_id = next_clue[0]["next_clue_id"]

    # Step 3: Check if the last clue was found on the "About" platform
    last_clue_details = db.execute("SELECT platform FROM clues WHERE id = ?", last_clue_id)

    if not last_clue_details:
        return apology("No details found for the last clue.", 404)

    last_clue_platform = last_clue_details[0]["platform"]

    # Skip repeating "About" and advance to the next platform hint
    if last_clue_platform == "About" and last_clue_id == 2:  # Assuming clue_id 2 is the first
        flash("Proceed to the Gallery platform.")
    else:
        # Get the next clue's details for regular hints
        next_clue_details = db.execute("SELECT * FROM clues WHERE id = ?", next_clue_id)

        if not next_clue_details:
            return apology("No clue found for the next clue ID.", 404)

        next_clue_info = next_clue_details[0]
        flash(f"You can find the next clue in the {next_clue_info['platform']} platform.")

    # Step 4: Add 10 minutes (600 seconds) to the total time
    additional_time = 600  # 10 minutes in seconds
    total_time_spent = accumulated_time + additional_time  # Add the additional time

    # Update the accumulated time in player_progress
    db.execute("UPDATE player_progress SET time_spent = ? WHERE user_id = ?",
               total_time_spent, user_id)

    # Update session to reflect the new total time
    session["accumulated_time"] = total_time_spent

    return redirect("/")  # Redirect back to the main page



@app.route("/about")
@login_required
def about():
    # Give a short introduction to the game
    return render_template("about.html")


@app.route("/clue_input", methods=["POST"])
@login_required
def clue_input():
    user_id = session["user_id"]
    what = sanitize_input(request.form.get("what"))
    platform = sanitize_input(request.form.get("platform"))

    # Check for required inputs
    if not what or not platform:
        return apology("Both clue and platform are required.")

    # Query the clues table for the entered clue
    matching_clues = db.execute(
        "SELECT * FROM clues WHERE what = ? AND platform = ? AND real_clue = 1", what, platform)

    if not matching_clues:
        return apology("Wrong clue! Try again!")

    # Get the first matching clue
    clue = matching_clues[0]
    clue_id = clue['id']
    required_clue_id = clue['required_clue_id']

    # Check if the clue has already been added to player_progress
    if db.execute("SELECT * FROM player_progress WHERE user_id = ? AND clue_id = ?", user_id, clue_id):
        flash("You have already found this clue.")
        return redirect("/")

    # Check if the required clue ID has been found by the player
    if required_clue_id is not None:
        found_required_clue = db.execute(
            "SELECT * FROM player_progress WHERE user_id = ? AND clue_id = ?", user_id, required_clue_id)

        # Ensure we require the clue before allowing progress
        if not found_required_clue:
            # Optional: Check if the required clue actually exists in the clues table
            required_clue_check = db.execute(
                "SELECT * FROM clues WHERE id = ?", required_clue_id)

            if not required_clue_check:
                return apology("Required clue does not exist in the database.")

            flash("You need to find another clue first!")
            return redirect("/")

    # Insert into player_progress if all checks pass
    db.execute("INSERT INTO player_progress (user_id, clue_id, platform, what) VALUES (?, ?, ?, ?)",
               user_id, clue_id, platform, what)

    # Update the `clues` table to mark the clue as found for all users
    db.execute("UPDATE clues SET is_found = 1 WHERE id = ?", clue_id)

    flash("Well done! Clue is correct!")

    # Check if all clues have been found for this user
    total_clues = db.execute("SELECT COUNT(*) FROM clues WHERE real_clue = 1")[0]['COUNT(*)']
    clues_found = db.execute(
        "SELECT COUNT(*) FROM player_progress WHERE user_id = ?", user_id)[0]['COUNT(*)']

    if clues_found == total_clues:
        return redirect("/endgame")

    return redirect("/")



# Check clue ID to see if access is granted to some pages
def check_clue_access(user_id, required_clue_id):
    """Check if user has the required clues to access a page."""
    if not required_clue_id:
        return True  # If no clues are required, grant access

    placeholders = ', '.join('?' for _ in required_clue_id)  # Create placeholders for the query
    clues_found = db.execute(f"""
        SELECT COUNT(*) AS count
        FROM player_progress
        WHERE user_id = ? AND clue_id IN ({placeholders})
    """, (user_id, *required_clue_id))[0]['count']  # Pass user_id and clue_ids

    return clues_found == len(required_clue_id)


def get_clue_ids(user_id):
    """Retrieve clue IDs for a user."""
    clue_ids = db.execute("SELECT clue_id FROM player_progress WHERE user_id = ?", user_id)
    return [row['clue_id'] for row in clue_ids]


def get_db_connection():
    """Establish a connection to the database."""
    try:
        conn = sqlite3.connect('game.db')  # Replace with your actual database file
        conn.row_factory = sqlite3.Row  # This enables accessing columns by name
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None  # Return None or raise an error


def calculate_rank(completion_time):
    """Calculate player's rank based on completion time."""
    conn = get_db_connection()
    if conn is None:
        return 1  # Default rank if connection fails

    try:
        scores = conn.execute(
            "SELECT completion_time FROM scoreboard ORDER BY completion_time").fetchall()
    finally:
        conn.close()

    # If there are no scores, return rank 1
    if not scores:
        return 1

    # Determine the player's rank based on completion time
    rank = 1  # Start from rank 1
    for score in scores:
        if score['completion_time'] < completion_time:  # Faster times mean better rank
            rank += 1
        elif score['completion_time'] == completion_time:  # Handle ties
            continue  # Don't increase rank for ties

    return rank

@app.template_filter()
def format_time(seconds):
    """Convert seconds to D:HH:MM:SS format."""
    days, remainder = divmod(seconds, 86400)  # 86400 seconds in a day
    hours, remainder = divmod(remainder, 3600)  # 3600 seconds in an hour
    minutes, seconds = divmod(remainder, 60)    # 60 seconds in a minute
    return f"{days}d {hours:02}h {minutes:02}m {seconds:02}s" if days > 0 else f"{hours}h {minutes:02}m {seconds:02}s"


def get_player_rank(user_id):
    """Retrieve the player's rank based on completion time."""

    # Get a connection to the database
    conn = get_db_connection()
    if conn is None:
        return None  # Handle case when the database connection fails

    try:
        # Fetch the player's completion time from the scoreboard
        player_time_row = conn.execute(
            "SELECT completion_time FROM scoreboard WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        # If the player has no recorded time, return None
        if player_time_row is None:
            return None

        player_time = player_time_row[0]

        # Fetch all players' times, sorted in ascending order (faster times = better rank)
        all_times = conn.execute(
            "SELECT completion_time FROM scoreboard ORDER BY completion_time ASC"
        ).fetchall()

        # Find the player's rank by comparing their time to others
        player_rank = 1
        for time_row in all_times:
            if time_row[0] < player_time:
                player_rank += 1
            else:
                break

        return player_rank

    except Exception as e:
        print(f"Database error: {e}")
        return None  # Handle errors by returning None or an appropriate default value

    finally:
        conn.close()


@app.route("/endgame", methods=["GET", "POST"])
@login_required
def endgame():
    """Show the endgame message and save player score."""
    user_id = session.get("user_id")

    conn = get_db_connection()
    if conn is None:
        return apology("Failed to connect to the database.")

    start_time = session.get('start_time')
    end_time = time.time() if start_time else None
    time_spent = int(end_time - start_time) if start_time else None

    # Calculate the player's rank based on the current completion time if time_spent is available
    player_rank = calculate_rank(time_spent) if time_spent is not None else None

    if request.method == "POST":
        player_name = sanitize_input(request.form.get("player_name"))

        if not player_name:
            return apology("Player name is required.")

        try:
            # Check for existing score
            existing_score = conn.execute(
                "SELECT COUNT(*) FROM scoreboard WHERE user_id = ?",
                (user_id,)
            ).fetchone()[0]

            if existing_score > 0:
                flash("You have already finished the game once. Your score won't be recorded again.")
                return redirect("/scoreboard")

            # Insert the player's score into the scoreboard
            conn.execute("INSERT INTO scoreboard (user_id, username, completion_time) VALUES (?, ?, ?)",
                         (user_id, player_name, time_spent))
            conn.commit()

            # Store the player's name in the session for later use
            session["current_player_name"] = player_name

            # Render the endgame page with the calculated player rank
            return render_template("endgame.html", player_rank=player_rank, username=player_name)

        except Exception as e:
            conn.rollback()  # Rollback on error
            return apology(f"Database error: {e}")
        finally:
            conn.close()

    # Handle GET request
    username_row = conn.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
    username = username_row[0] if username_row else "Guest"

    # Render the endgame page with the current player rank if available
    return render_template("endgame.html", player_rank=player_rank, username=username)


@app.route("/legacy", methods=["GET", "POST"])
@login_required
def legacy():
    """Show the endgame message and save player score."""
    user_id = session.get("user_id")

    # Fetch the player's current rank before any POST request (on GET or page load)
    # Assume this function retrieves the player's current rank
    player_rank = get_player_rank(user_id)

    # If GET request, fetch username
    conn = get_db_connection()
    username_row = conn.execute(
        "SELECT username FROM scoreboard WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()

    # Extract username from the row if it exists
    username = username_row[0]

    # Render the endgame page
    return render_template("legacy.html", player_rank=player_rank, username=username)


@app.route("/scoreboard")
@login_required
def scoreboard():
    user_id = session.get("user_id")

    # Get a connection to the database
    conn = get_db_connection()
    # Fetching user_id along with username and completion_time
    scores = conn.execute("SELECT user_id, username, completion_time FROM scoreboard").fetchall()
    conn.close()

    # Ensure scores are passed to the template correctly
    print(scores)  # Debugging to check the structure of scores

    return render_template("scoreboard.html", scores=scores, current_user_id=user_id)


@app.route("/fakebook", methods=["GET", "POST"])
@login_required
def fakebook():
    """Show Fakebook clues"""

    if request.method == "POST":
        # Retrieve name, username, and password from form
        name = sanitize_input(request.form.get("name"))
        username = sanitize_input(request.form.get("username"))
        password = sanitize_input(request.form.get("password"))

        if not username or not password or not name:
            return apology("All fields are required.")

        # Check if player has clues 2, 3, and 4
        user_id = session["user_id"]
        clues_required = [2, 3, 4]
        clues_found = db.execute("""
            SELECT COUNT(*) AS count
            FROM player_progress
            WHERE user_id = ? AND clue_id IN (?,?,?)
        """, user_id, *clues_required)[0]['count']

        if clues_found < len(clues_required):
            return apology("You need to find your friend's name and the login credentials.")

        # Get the matching friend's credentials from the database
        friends = db.execute("SELECT * FROM friends WHERE friend_name = ?", name)

        if not friends:
            return apology("No friends found.")

        friend = friends[0]
        f_username = friend["fakebook_username"]
        f_password = friend["fakebook_password"]

        if f_username != username:
            return apology("Invalid username.")
        if f_password != password:
            return apology("Invalid password.")

        # Store the username and password in the session
        session["fakebook_username"] = username
        session["fakebook_password"] = password

        # Render the Fakebook page with clues
        return render_template("fakebook.html")

    else:
        # If already logged in, use the stored session credentials
        if "fakebook_username" in session and "fakebook_password" in session:
            return render_template("fakebook.html")

        # Otherwise, prompt for login
        return render_template("fakebook_login.html")


def check_progress(user_id):
    """Check progress for a given user."""
    try:
        conn = sqlite3.connect('game.db')  # Ensure the database connection is correct
        cursor = conn.cursor()

        # Correctly passing user_id as a single-element tuple
        cursor.execute("SELECT what FROM player_progress WHERE user_id = ?", (user_id,))

        progress = cursor.fetchall()

        conn.close()
        return progress
    except sqlite3.Error as e:
        print(f"Database error: {e}")  # Error handling
        return None


@app.route("/quacker", methods=["GET", "POST"])
@login_required
def quacker():
    """Show Quacker clues"""
    if request.method == "POST":
        # Retrieve name, username, and password from form
        name = sanitize_input(request.form.get("name"))
        username = sanitize_input(request.form.get("username"))
        password = sanitize_input(request.form.get("password"))

        if not username or not password or not name:
            return apology("All fields are required.")

        # Check if player has clues 6, 7, and 8
        user_id = session["user_id"]
        clues_required = [6, 7, 8]
        clues_found = db.execute("""
            SELECT COUNT(*) AS count
            FROM player_progress
            WHERE user_id = ? AND clue_id IN (?,?,?)
        """, user_id, *clues_required)[0]['count']

        if clues_found < len(clues_required):
            return apology("You need to find your friend's name and the login credentials.")

        # Get the matching friend's credentials from the database
        friends = db.execute("SELECT * FROM friends WHERE friend_name = ?", name)

        if len(friends) != 1:
            return apology("No friend found.")

        friend = friends[0]
        q_username = friend["quacker_username"]
        q_password = friend["quacker_password"]

        if q_username != username:
            return apology("Invalid username.")
        if q_password != password:
            return apology("Invalid password.")

        # Store the username and password in the session
        session["quacker_username"] = username
        session["quacker_password"] = password

        # Render the Fakebook page with clues
        return render_template("quacker.html")

    else:
        # If already logged in, use the stored session credentials
        if "quacker_username" in session and "quacker_password" in session:
            return render_template("quacker.html")

        # Otherwise, prompt for login
        return render_template("quacker_login.html")


@app.route("/instaquam", methods=["GET", "POST"])
@login_required
def instaquam():
    """Show Instaquam clues"""

    if request.method == "POST":
        # Retrieve name, username, and password from form
        name = sanitize_input(request.form.get("name"))
        username = sanitize_input(request.form.get("username"))
        password = sanitize_input(request.form.get("password"))

        if not username or not password or not name:
            return apology("All fields are required.")

        # Check if player has clues 9, 10, and 12
        user_id = session["user_id"]
        clues_required = [9, 10, 12]
        clues_found = db.execute("""
            SELECT COUNT(*) AS count
            FROM player_progress
            WHERE user_id = ? AND clue_id IN (?,?,?)
        """, user_id, *clues_required)[0]['count']

        if clues_found < len(clues_required):
            return apology("You need to find your friend's name and the login credentials.")

        # Get the matching friend's credentials from the database
        friends = db.execute("SELECT * FROM friends WHERE friend_name = ?", name)

        if len(friends) != 1:
            return apology("No friend found.")

        friend = friends[0]
        i_username = friend["instaquam_username"]
        i_password = friend["instaquam_password"]

        if i_username != username:
            return apology("Invalid username.")
        if i_password != password:
            return apology("Invalid password.")

        # Store the username and password in the session
        session["instaquam_username"] = username
        session["instaquam_password"] = password

        # Render the Fakebook page with clues
        return render_template("instaquam.html")

    else:
        # If already logged in, use the stored session credentials
        if "instaquam_username" in session and "instaquam_password" in session:
            return render_template("instaquam.html")

        # Otherwise, prompt for login
        return render_template("instaquam_login.html")


@app.route("/gallery")
@login_required
def gallery():
    user_id = session.get('user_id')  # Assuming user_id is stored in the session
    clue_ids = get_clue_ids(user_id) if user_id else []
    return render_template('gallery.html', clue_ids=clue_ids)


@app.route("/newspaper")
@login_required
def newspaper():
    """Show Newspaper clues"""
    user_id = session.get('user_id')  # Assuming user_id is stored in the session
    clue_ids = get_clue_ids(user_id) if user_id else []
    return render_template("newspaper.html", clue_ids=clue_ids)


@app.route("/hotel")
@login_required
def hotel():
    """Show hotel clues"""
    user_id = session.get('user_id')  # Assuming user_id is stored in the session
    clue_ids = get_clue_ids(user_id) if user_id else []
    return render_template('hotel.html', clue_ids=clue_ids)


@app.route("/bar")
@login_required
def bar():
    """Bar page content based on clues and chat functionality"""
    user_id = session["user_id"]

    # Check if player has clue 10
    user_id = session["user_id"]
    clues_required = [10]
    clues_found = db.execute("""
                             SELECT COUNT(*) AS count
                             FROM player_progress
                             WHERE user_id = ? AND clue_id IN (?)""", user_id, *clues_required)[0]['count']

    if clues_found < len(clues_required):
        return apology("Sorry, you’re too tipsy to enter. Better hydrate first—don't want you making any pour decisions!")
    return render_template("bar.html")


@app.route("/beach")
@login_required
def beach():
    """Show beach clues"""
    return render_template("beach.html")


@app.route("/tattoo")
@login_required
def tattoo():
    """Show Dark Wing Tattoo clues"""
    user_id = session["user_id"]

    # Check if the required clue_id (replace with the actual clue_id for tattoo) is in player_progress
    required_clue_ids = 11  # Required clue_id needed to access tattoo.html
    clue_found = db.execute("""
        SELECT * FROM player_progress WHERE user_id = ? AND clue_id = ?
    """, user_id, required_clue_ids)

    if not clue_found:
        return apology("First, you need to ask your friend where he is.")

    return render_template("tattoo.html")


@app.route("/party")
@login_required
def party():
    """Show Beach Night Club clues"""
    user_id = session["user_id"]

    # Check if the required clue_id (replace with the actual clue_id for party) is in player_progress
    required_clue_id = 20  # Required clue_id needed to access party.html
    clue_found = db.execute("""
        SELECT * FROM player_progress WHERE user_id = ? AND clue_id = ?
    """, user_id, required_clue_id)

    if not clue_found:
        return apology("It's not quite party o'clock yet.")

    return render_template("party.html")


@app.route("/motto")
@login_required
def motto():
    """Show beach clues"""
    return render_template("motto.html")


# Run the app
if __name__ == "__main__":
    app.run
