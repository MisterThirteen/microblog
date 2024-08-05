from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# importing flask login to manage user logins
from flask_login import LoginManager

# for logging errors by email
import logging
from logging.handlers import SMTPHandler

# for logging errors to a file
from logging.handlers import RotatingFileHandler
import os

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


# setting functionality to enable error logging by email by creating a SMTPHandler instance
# only going to enable the email logger when the application is running without debug mode
if not app.debug:
    # also only enabling this when the email server exists in the configuration
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        # setting its level so that it only reports errors and not warnings, informational or debugging messages
        mail_handler.setLevel(logging.ERROR)
        # attaching to the app.logger object from Flask
        app.logger.addHandler(mail_handler)


    # the if statement below provides functionality for logging errors to a file
    # creating the logs folder if it doesn't exist yet
    if not os.path.exists('logs'):
        os.mkdir('logs')

    #using RotatingFileHandler to rotate the logs, ensuring that the log files do not grow too large when the application runs for a long time
    file_handler = RotatingFileHandler(
        'logs/microblog.log',# writing the log file with name microblog.log in a logs directory
        maxBytes=10240,#limiting the size of the log file to 10KB
        backupCount=10)#keeping only the last 10 log files as backup
    
    # The logging.Formatter class provides custom formatting for the log messages.
    # Since these messages are going to a file, I want them to have as much information as possible.
    # So I'm using a format that includes the timestamp, the logging level, the message and the source file and line number from where the log entry originated.
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))

    # To make the logging more useful, I'm also lowering the logging level to the INFO category, both in the application logger and the file logger handler.
    # The logging categories are DEBUG, INFO, WARNING, ERROR and CRITICAL in increasing order of severity.
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')

from app import routes, models, errors