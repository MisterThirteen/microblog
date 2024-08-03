import os

# specifying the base directory
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # specifying path for the SQLite database
    # In this case I'm taking the database URL from the DATABASE_URL environment variable,
    # and if that isn't defined, I'm configuring a database named app.db located in the main directory of the application, 
    # which is stored in the basedir variable
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    
