# Centralised module to manage routes throughout the web application

from flask import render_template, flash, redirect, url_for, request

from urllib.parse import urlsplit

from app import app

#importing forms
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm

# importing modules required for user login routing
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import db


from app.models import User, Post

# importing datetime for datetime stamps, particularly to record when a user was last seen
from datetime import datetime, timezone


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():

    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))

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
        title='Home Page',
        form=form,
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

# creating user profile page route and functionality.
# This time we have a dynamic component in the route, which is indicated as the <username> URL component that is surrounded by < and >. 
# When a route has a dynamic component, Flask will accept any text in that portion of the URL, 
# and will invoke the view function with the actual text as an argument. For example, if the client browser requests URL /user/susan, 
# the view function is going to be called with the argument username set to 'susan'
@app.route('/user/<username>')
@login_required
def user(username):#username argument is provided when user clicks on the 'Profile' button on the navbar. See base.html file

    # db.first_or_404() works like scalar() when there are results, but in the case that there are no results it automatically sends 
    # a 404 error back to the client. By executing the query in this way I save myself from checking if the query returned a user, 
    # because when the username does not exist in the database the function will not return and instead a 404 exception will be raised.
    user = db.first_or_404(sa.select(User).where(User.username == username))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}        
    ]

    # Rendering the follow or unfollow button by  instantiateing an EmptyForm object and pass it to the user.html template.
    # Because these two actions are mutually exclusive, we can pass a single instance of this generic form to the template
    # For more info on the follow and unfollow methods, see follow routing method in routes.py
    # Also can see follow and unfollow methods in User class in methods.py
    form = EmptyForm()


    return render_template('user.html', user=user, posts=posts, form=form)


# The @before_request decorator from Flask register the decorated function to be executed right before the view function
# This is extremely useful because now I can insert code that I want to execute before any view function in the application, and I can have it in a single place.
@app.before_request
def before_request():

    # checks if the current_user is logged in, and in that case sets the last_seen field to the current time
    if current_user.is_authenticated:

        # a server application needs to work in consistent time units, and the standard practice is to use the UTC time zone.
        # It is not recommended to use local time
        current_user.last_seen = datetime.now(timezone.utc)

        # We can also specify db.session.add() before db.session.commit(), but it is not required here
        # This is because when you reference current_user, Flask-Login will invoke the user loader callback function, 
        # which will run a database query that will put the target user in the database session. 
        # So you can add the user again in this function, but it is not necessary because it is already there.
        db.session.commit()


# Routing for edit_profile.html and EditProfileForm
@app.route('/edit_profile', methods = ['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)

    # If validate_on_submit() returns True I copy the data from the form into the user object and then write the object to the database
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved')

        return redirect(url_for('edit_profile'))
    
    # when validate_on_submit() returns False it can be due to two different reasons. We need to treat these two cases separately.
    # First, it can be because the browser just sent a GET request. We respond to this by providing an initial version of the form template (by having the current stored data pre-filled in the fields)
    # Second reason can also be when the browser sends a POST request with form data, but something in that data is invalid.
    elif request.method == 'GET':#checking request.method to distinguish between these two cases
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title='Edit Profile', form=form)


# Routing for following another user
# Unlike other forms such as the login and edit profile forms, these two forms do not have their own pages,
# the forms will be rendered by the user() route and will appear in the user's profile page.
# The only reason why the validate_on_submit() call can fail is if the CSRF token is missing or invalid, so in that case we just redirect the application back to the home page.
# To render the follow or unfollow button, weq need to instantiate an EmptyForm object and pass it to the user.html template.
@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()

    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username)
        )

        # some error checking before actually carrying out the follow or unfollow action.
        # This is to prevent unexpected issues, and to try to provide a useful message to the user when a problem has occurred.
        if user is None:
            flash(f'User {username} not found')
            return redirect(url_for('index'))        
        if user == current_user:
            flash('You cannot follow yourself')
            return redirect(url_for('user', username=username))
        
        # using follow method from User model to follow another user
        current_user.follow(user)
        db.session.commit()
        flash(f'You are following {username}!')
        return redirect(url_for('user', username=username))
    
    else:
        return redirect(url_for('index'))
    
# Routing for unfollowing another user
# Similar to routing for following another user. Refer to 'follow' method in routes.py for comments and info
@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username)
        )

        if user is None:
            flash(f'User {username} not found')
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        
        # Method for this user to unfollow the other user
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are not following {username}')
        return redirect(url_for('user', username=username))
    
    else:
        return redirect(url_for('index'))