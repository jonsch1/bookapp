import os
import csv
import requests
import simplejson as json
from flask import Flask, session, flash, redirect, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import apology
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from flask import jsonify



app = Flask(__name__)
os.environ["DATABASE_URL"] = "postgres://rihwzyhaltmydz:2ee8e5f0380167cae24e01ee411f18526a71c928aaa47847c11bd9b31a3d3ba3@ec2-54-247-125-116.eu-west-1.compute.amazonaws.com:5432/d3sqngohgn6ob4"

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
# api key AlYz0XYp89FroGuNfI25OA
#db.execute("CREATE TABLE users (user_id SERIAL PRIMARY KEY,user_name VARCHAR(100) NOT NULL,user_password VARCHAR(100) NOT NULL);")


@app.route("/")
def index():
    return render_template("homepage.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # check if username and passwords are provided and match
        if not request.form.get("username"):
            return apology("must provide username", 403)
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        elif (request.form.get("password") != request.form.get("password-verification")):
            return apology("passwords do not match", 403)

        # encrypt password
        hash = generate_password_hash(request.form.get(
            "password"), method='pbkdf2:sha256', salt_length=8)
        print("test1")
        # write new user in db

        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": request.form.get("username")}).fetchall()
        db.commit()
        # if username already exists:
        if (len(rows) > 0):
            return apology("username already exists", 403)

        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", {
                   "username": request.form.get("username"), "hash": hash})
        db.commit()
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": request.form.get("username")}).fetchall()
        # Remember which user has logged in
        db.commit()
        session["username"] = request.form.get("username")

        # log in new user
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)
            print("test1")
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
            print("test2")
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": request.form.get("username")}).fetchall()
        db.commit()
        print(rows)
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]
        session["username"] = rows[0]["username"]
        print(session["username"])
        # Redirect user to home page
        return redirect("/")

# User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/book/<int:book_id>", methods=["GET", "POST"])
def book(book_id):
    # ensure that user is logged in
    if session.get("username") is None:
        return redirect("/login")
    else:
        book = db.execute("SELECT * FROM books WHERE book_id=:book_id",
                          {"book_id": book_id}).fetchone()
        bookreviews = db.execute(
            "SELECT * FROM reviews WHERE book_id=:book_id", {"book_id": book_id}).fetchall()
        db.commit()
        isbn = book.isbn
        print("hallo", session["username"])
        username = session["username"]
        print(isbn)
        goodreads_data = requests.get("https://www.goodreads.com/book/review_counts.json", params={
                                      "key": "AlYz0XYp89FroGuNfI25OA", "isbns": f"{isbn}"}).json()
        print(goodreads_data)

        if request.method == "GET":
            return render_template("book.html", bookreads=goodreads_data, book=book, bookreviews=bookreviews)

        else:

            print(session["username"])
            print("HELLO")
            text = request.form.get("text")
            rating = request.form.get("rating")
            # make sure user doesn't make multiple reviews -> db response must equal none
            if not (db.execute("SELECT * from reviews WHERE user_name=:username AND book_id=:book_id", {"username": username, "book_id": book_id}).fetchall()):
                # WRITE REVIEW INTO DB
                db.execute("INSERT INTO reviews (review_text, review_rating, user_name, book_id) VALUES(:review_text, :review_rating, :user_name, :book_id); ", {
                           "review_text": text, "review_rating": rating, "user_name": username, "book_id": book_id})
                db.commit()
                # UPDATE AVERAGE RATING IN BOOK TABLE
                if(db.execute("SELECT average_rating FROM books WHERE book_id=:book_id", {"book_id": book_id}).fetchall() != "NULL"):
                    average_rating = db.execute("SELECT AVG(review_rating) FROM reviews WHERE book_id=:book_id;", {
                                                "book_id": book_id}).fetchall()[0][0]
                    print(average_rating)
                    db.commit()
                db.execute("UPDATE books SET average_rating=:average_rating WHERE book_id=:book_id;", {
                           "book_id": book_id, "average_rating": average_rating})
                db.commit()
                return redirect(f"/book/{book_id}")

            return ("Du kannst nicht mehrere Reviews machen")


@app.route("/search", methods=["GET", "POST"])
def search():
    if session.get("username") is None:
        return redirect("/login")
    """Get stock quote."""
    # get symbol from html form

    # execute lookup(symbol)
    if request.method == "POST":
        if not (request.form.get("symbol")):
            return apology("Must put in some isbn")
        else:
            name = request.form.get("symbol")
            matches = db.execute(
                "SELECT * FROM books WHERE title LIKE CONCAT('%', :name, '%') OR isbn LIKE CONCAT('%', :name, '%') OR author LIKE CONCAT('%', :name, '%')", {"name": name}).fetchall()
            db.commit()
            if matches:
                return render_template("searched.html", matches=matches)
            else:
                return apology("Couldn't find matching books")
    else:
        return render_template("search.html")


@app.route("/api/<isbn>", methods=["GET"])
def api(isbn):

    bookinformation = db.execute(
        "SELECT * FROM books WHERE isbn=:isbn;", {"isbn": isbn}).fetchall()
    db.commit()
    # get relevant information from database response
    isbn = bookinformation[0][1]
    title = bookinformation[0][2]
    author = bookinformation[0][3]
    year = bookinformation[0][4]
    rating = bookinformation[0][5]
    print(rating)
    if not rating:
        rating = "ALALALALONG"
    # generate json response
    return (jsonify({
        "isbn": isbn,
        "title": title,
        "author": author,
        "year": year,
        "rating": rating,
    }))
