"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, jsonify, render_template, request, flash, redirect,
                   session)
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = 'ABC'

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template('homepage.html')


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template('user_list.html', users=users)


@app.route('/register')
def register():
    """Register form"""

    return render_template('register_form.html')


@app.route('/register', methods=['POST'])
def process_register():
    """Process register information"""

    email = request.form.get('email')
    password = request.form.get('password')

    if User.query.filter_by(email=email).all():
        print "The user is already there."
    else:
        db.session.add(User(email=email, password=password))
        db.session.commit()
        print "The user email and password has been added to DB."

    print 'Email: {}'.format(request.form.get('email'))
    return redirect('/')


@app.route('/login')
def login():
    """Shows a log-in form."""

    return render_template('/login_form.html')


@app.route('/login', methods=['POST'])
def process_login():
    """Process the log-in form"""

    email = request.form.get('email')
    password = request.form.get('password')

    # TODO : Consider later
    # Make sure it is first time for the user to login

    # throw an error if the user is not ther ('user='' part tried)
    try:
        user = User.query.filter_by(email=email).one()

        # if it is first time, then check authentification
        if password == user.password:
            flash(email + ' logged in')
            session['user'] = email
            print session
            return redirect('/')

    # if not authentificated, then do not login the user
    except:
        return redirect('/')


if __name__ == '__main__':
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
