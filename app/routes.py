# Centralised module to manage routes throughout the web application

from flask import render_template, flash, redirect, url_for, request

from urllib.parse import urlsplit

from app import app

#importing forms
from app.forms import LoginForm, RegistrationForm

# importing modules required for user login routing
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import db
from app.models import User

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username':'Miguel'}

    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]

    # return('hey there')
    return render_template(
        'index.html',
        title='Home',
        posts=posts
    )
        

@app.route('/login', methods=['GET', 'POST'])
def login():

    # user authentication check if statement
    # The current_user variable comes from Flask-Login, and can be used at any time during the handling of a request
    # to obtain the user object that represents the client of that request. The value of this variable can be a user object
    # from the database (which Flask-Login reads through the user loader callback specified in models.py --> see  load_user(id) function),
    # or a special anonymous user object if the user did not log in yet.
    if current_user.is_authenticated:

        # if user is already logged in, but somehow navigates to the /login URL of the app, we redirect them to index
        return redirect(url_for('index'))

    #using the LoginForm class to create a form
    form = LoginForm()

    #accept and validate user submitted data for login
    if form.validate_on_submit():

        # old code for debugging. used flash messages in place of actually logging the user in,
        # while user models did not exist at the time
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data
        )
        )

        # uses submitted login form data to check db and load user data if it is a match
        # calling db.session.scalar(), will return the user object if it exists, or None.
        # IMPORTANT! The db.session.scalar() method assumes there is only going to be one or zero results
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))

        # checks if user does not exist. if user does exist, checks if password provided is valid
        # returns True if either of these conditions are met, and flashes error message
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')

            # redirecting user to login when if the conditions above are met
            return redirect(url_for('login'))
        
        # if username and password are both correct, call the login_user() function, which comes from Flask-Login. This function will register the user as logged in,
        # so that means that any future pages the user navigates to will have the current_user variable set to that user.
        login_user(user, remember=form.remember_me.data)

        # Right after the user is logged in by calling Flask-Login's login_user() function, the value of the next query string argument is obtained.
        # Flask provides a request variable that contains all the information that the client sent with the request.
        # In particular, the request.args attribute exposes the contents of the query string in a friendly dictionary format.        
        next_page = request.args.get('next')

        # If the login URL does not have a next argument, then the user is redirected to the index page.
        # To determine if the URL is absolute or relative (to protect from attackers), parse with Python's urlsplit() function and then check if the netloc component is set or not.
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')

        # redirect the newly logged in user
        # If the login URL includes a next argument that is set to a relative path (or in other words, a URL without the domain portion), then the user is redirected to that URL.
        return redirect(next_page)

    return render_template(
        'login.html',
        title='Sign In',
        form=form#passing the form object to be used in the login.html 
    )


# routing and functionality to allow users to log out
@app.route('/logout')
def logout():

    # logging out is done by Flask-Login through the logout_user() function
    logout_user()
    return redirect(url_for('index'))


# routing and functionality to allow users to register
@app.route('/register', methods=['GET', 'POST'])
def register():

    # Check to make sure user is not already logged in.
    # If they are, redirect them to the index page
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()

    # creates a new user with the username, email and password provided
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)

        # writes the new user data to the database
        db.session.add(user)
        db.session.commit()
        
        flash('Congratulations, you are now a registered user!')

        # redirect to the login prompt so the user can log in
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)