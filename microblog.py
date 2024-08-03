# This module is the Python script at the top-level that defines the Flask application instance.
# For this application, we call this script microblog.py, and define it as a single line that imports the application instance.

import sqlalchemy as sa
import sqlalchemy.orm as so

# The from app import app statement imports the app variable that is a member of the app package.
from app import app, db
from app.models import User, Post

# The app.shell_context_processor decorator registers the function as a shell context function.
# When the flask shell command runs, it will invoke this function and register the items returned by it in the shell session.
# After you add the shell context processor function you can work with database entities without having to import them
@app.shell_context_processor
def make_shell_context():

    # The reason the function returns a dictionary and not a list is that for each item you have to also provide
    # a name under which it will be referenced in the shell, which is given by the dictionary keys.
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Post': Post}
