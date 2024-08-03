from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

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


from app import routes, models