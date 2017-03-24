"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
import correlation

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id,
                                               self.email)

    def similarity(self, other):
        """Return Pearson rating for user compared to other user."""

        self_ratings = {}
        paired_ratings = []

        for rating in self.ratings:
            self_ratings[rating.movie_id] = rating

        for rating in other.ratings:
            self_rating = self_ratings.get(rating.movie_id)
            if self_rating:
                paired_ratings.append((self_rating.score, rating.score))

        if paired_ratings:
            return correlation.pearson(paired_ratings)

        else:
            return 0.0

    def predict_rating(self, movie):
        """Predict rating for a movie."""

        ratings = movie.ratings

        similarities = [(self.similarity(rating.user), rating.score)
                        for rating in ratings]

        similarities.sort(reverse=True)

        numerator = sum([score * similarity for similarity, score in
                         similarities])
        denominator = sum([similarity for similarity, score in
                           similarities])

        return numerator * denominator


##############################################################################
# Movie classes
class Movie(db.Model):
    """Movie class"""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(90), nullable=True)
    released_at = db.Column(db.DateTime, nullable=True)
    imdb_url = db.Column(db.String(200), nullable=True)

    # must run python create_all() if newly generated
    # have space between fields and dependancies
    ratings = db.relationship('Rating')


##############################################################################
# Rating model class
class Rating(db.Model):
    """Rating class"""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    # check if /d and key is recognized as foregn (but do create_all() first)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    score = db.Column(db.Integer, nullable=True)

    movie = db.relationship('Movie')
    user = db.relationship('User', backref=db.backref('ratings',
                                                      order_by=rating_id))

    def __repr__(self):
        """Provide helpful representation when printed"""

        return "<Ratings user_id=%s, movie_id=%s>" % (self.user_id, self.movie_id)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
