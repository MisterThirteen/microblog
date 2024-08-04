from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# importing flask login to manage user logins
from flask_login import LoginManager

# Specifying the app variable as a Flask instance
# Note that this line below is the second 'app' in every line that says "from app import app"
app = Flask(__name__)

#telling Flask to read and apply the config class
#thus instead of just going ---> app.config['SECRET_KEY'] = 'asddfaef'
#we instead have it in the config class, in one neat compartment.
app.config.from_object(Config)


# specifying the database object
db = SQLAlchemy(app)
# specifying the database migration engine
migrate = Migrate(app, db)

# initialising flask login extension
# similar to other extensions, Flask-Login needs to be created and initialized right after the application instance in app/__init__.py
login = LoginManager(app)

# The 'login' value below is the function (or endpoint) name for the login view.
# In other words, the name you would use in a url_for() call to get the URL.
# The way Flask-Login protects a view function against anonymous users is with a decorator called @login_required.
# When you add this decorator to a view function below the @app.route decorator from Flask,
# the function becomes protected and will not allow access to users that are not authenticated.
# see the index route in routes.py for an example
login.login_view = 'login'




from app import routes, models