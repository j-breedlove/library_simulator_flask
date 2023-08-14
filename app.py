from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///books-collection.db"
db = SQLAlchemy(app)


# Database model for books
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Book {self.title}>'

    def add_book(self, title, author, rating):
        '''Add a book to the database. If the book already exists, print a message.'''
        book = db.session.query(Book).filter_by(title=title).first()
        if book is None:
            new_book = Book(title=title, author=author, rating=rating)
            db.session.add(new_book)
            db.session.commit()
        else:
            print(f"Book {title} already exists in the database.")
        return book

    def delete_book(self, id):
        '''Delete a book from the database using its ID.'''
        book = db.session.query(Book).filter_by(id=id).first()
        if book is None:
            print(f"Book {id} does not exist in the database.")
        else:
            db.session.delete(book)
            db.session.commit()
        return book


@app.route('/')
def home():
    '''Display the homepage with a list of all books.'''
    # Create the database if it doesn't exist.
    if not db:
        db.create_all()
    all_books = db.session.query(Book).all()
    if len(all_books) == 0:
        return render_template("index.html", books=all_books, empty=True)
    else:
        return render_template("index.html", books=all_books, empty=False)


@app.route("/add", methods=["GET", "POST"])
def add():
    '''Add a new book to the collection.'''
    error_message = None

    if request.method == "POST":
        title = request.form.get('book_title')
        author = request.form.get('book_author')
        rating_str = request.form.get('book_rating')

        try:
            rating = float(rating_str)

            # Ensure rating is between 0 and 10
            if 0 <= rating <= 10:
                Book().add_book(title, author, rating)
                return redirect(url_for("home"))
            else:
                error_message = "Invalid rating. Please enter a number between 0 and 10."
        except ValueError:
            error_message = "Invalid rating. Please enter a number."

    return render_template("add.html", error_message=error_message)


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    '''Edit the rating of a book.'''
    book_to_update = Book.query.get(id)
    if request.method == "POST":
        new_rating = request.form['new_rating']
        if book_to_update is not None:
            book_to_update.rating = float(new_rating)
            db.session.commit()
            print(f"Updated rating for {book_to_update.title} to {book_to_update.rating}")
        else:
            print(f"Book with id {id} does not exist in the database.")
        return redirect(url_for("home"))
    return render_template("edit.html", book=book_to_update)


@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete(id):
    '''Delete a book from the collection.'''
    book = Book()
    book.delete_book(id)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
