# Project 1

Web Programming with Python and JavaScript

Datenbank Befehle:
@app.route("/database")
def books():#loads all the books into database
    db.execute("CREATE TABLE books (book_id SERIAL PRIMARY KEY,isbn VARCHAR(100),title VARCHAR(100),author VARCHAR(100),year VARCHAR(100) );")
    f= open("books.csv")
    reader=csv.reader(f)
    for isbn,title,author,year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES(:isbn, :title, :author, :year)", {"isbn":isbn, "title":title, "author":author,"year":year})
        db.commit()
        print("tes")
    return "yay"
    db.execute("ALTER TABLE books ADD average_rating DECIMAL;")
    db.commit()

    db.execute("ALTER TABLE books ALTER COLUMN average_rating decimal(5,2);")
    db.commit()
@app.route("/reviews")
    def reviews():
      db.execute("DROP TABLE reviews;")
      db.execute("CREATE TABLE reviews (book_id INTEGER, user_name VARCHAR(100), review_text VARCHAR(5000), review_rating INTEGER);")
      db.commit()


    Book Page: When users click on a book from the results of the search page, they should be taken to a book page, with details about the book: its title, author, publication year, ISBN number, and any reviews that users have left for the book on your website.

    Review Submission: On the book page, users should be able to submit a review: consisting of a rating on a scale of 1 to 5, as well as a text component to the review where the user can write their opinion about a book. Users should not be able to submit multiple reviews for the same book.

    Goodreads Review Data: On your book page, you should also display (if available) the average rating and number of ratings the work has received from Goodreads.
