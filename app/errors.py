# Custom error handlers

from flask import render_template
from app import app, db


# Flask provides a mechanism for an application to install its own error pages,
# so that users don't have to see the plain and boring default ones.
# below is an example error handler for 404 errors, which are common

# error functions work very similarly to view functions
@app.errorhandler(404)
def not_found_error(error):
    # returning the contents of their respective templates (in this case, 404.html)
    # Note that the function returns a second value after the template, which is the error code number (in this case 404)
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):

    # The error handler for the 500 errors could be invoked after a database error, which was actually the case with the username duplicate above. 
    # To make sure any failed database sessions do not interfere with any database accesses triggered by the template, I issue a session rollback. 
    # This resets the session to a clean state.
    db.session.rollback()
    return render_template('500.html'), 500