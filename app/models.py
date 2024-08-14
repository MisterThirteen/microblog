# Python module that defines the database models required

# importing werkzeug for password security
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime, timezone
from typing import Optional
# sqlalchemy module includes general purpose database functions and classes such as types and query building helpers
import sqlalchemy as sa
# sqlalchemy.orm provides the support for using models
import sqlalchemy.orm  as so

#importing the database instance from flask sqlalchemy
from app import db

# importing 
from app import login

#importing UserMixin to simplify user authentication for flask login
from flask_login import UserMixin

# importing hashlib md5 for profile avatars
from hashlib import md5


# class to initialise followers association
# It is important that this is added ABOVE the User model in models.py, so that the User model can reference it
# sa.Table class from SQLAlchemy directly represents a database table
followers = sa.Table(
    'followers',#The table name is given as first argument.
    db.metadata,#second argument is that metadata, the place where SQLAlchemy stores the information about all the tables in the database. When using Flask-SQLAlchemy, the metadata instance can be obtained with db.metadata
    # For this table neither of the foreign keys will have unique values that can be used as a primary key on their own, but the pair of foreign keys combined is going to be unique. For that reason both columns are marked as primary keys. This is called a compound primary key.
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),# The columns of this table are instances of sa.Column initialized with the column name, type and options
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True)
)




# class to represent users stored in the database
# The class inherits from db.Model, a base class for all models from Flask-SQLAlchemy.
# The User model defines several fields as class variables.
# These are the columns that will be created in the corresponding database table.
class User(UserMixin, db.Model):

    # In most cases defining a table column requires more than the column type.
    # SQLAlchemy uses a so.mapped_column() function call assigned to each column to provide this additional configuration.
    # In the case of id below, the column is configured as the primary key.
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    # Fields are assigned a type using Python type hints, wrapped with SQLAlchemy's so.Mapped generic type.
    # A type declaration such as so.Mapped[int] or so.Mapped[str] define the type of the column,
    # and also make values required (i.e.  non-nullable in database terms)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)

    # For string columns many databases require a length to be given, so this is also included.
    #  have included other optional arguments that allow me to indicate which fields are unique and indexed,
    # which is important so that the database is consistent and searches are efficient
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)

    # To define a column that is allowed to be empty or nullable,
    # the Optional helper from Python is also added, as password_hash demonstrates
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    # def __repr__(self) -> str:
    #     return super().__repr__()


    # The User class will have a 'posts' field, that is initialized with so.relationship() below.
    # This is not an actual database field, but a high-level view of the relationship between users and posts
    # The posts relationship attribute uses a different typing definition. Instead of so.Mapped, the posts field uses so.WriteOnlyMapped, which defines posts as a collection type with Post objects inside.
    # The first argument to so.relationship() is the model class that represents the other side of the relationship. This argument can be provided as a string (i.e. 'Post'), which is necessary when the class is defined later in the module.
    posts: so.WriteOnlyMapped['Post'] = so.relationship(

        # The back_populates arguments reference the name of the relationship attribute on the other side (i.e. author <-> posts),
        # so that SQLAlchemy knows that these attributes refer to the two sides of the same relationship.
        back_populates='author'
    )


    # Function that allows the user to set their password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    
    # Function that checks user entered password against saved password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    # The __repr__ method tells Python how to print objects of this class,
    # which is going to be useful for debugging.
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    # The avatar() method (see below) of the User class returns the URL of the user's avatar image, scaled to the requested size in pixels. 
    # For users that don't have an avatar registered, an "identicon" image will be generated. To generate the MD5 hash, 
    # I first convert the email to lower case, as this is required by the Gravatar service. 
    # Then, because the MD5 support in Python works on bytes and not on strings, 
    # I encode the string as bytes before passing it on to the hash function.
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()

        # By making the User class responsible for returning avatar URLs is that if some day I decide Gravatar avatars are not what I want, 
        # I can just rewrite the avatar() method to return different URLs, and all the templates will start showing the new avatars automatically
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
    

    # Optional fields for users to provide some information about themselves
    # The string length of 140 characters is enforced in the form validation
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc)
        )
    

    # follower functionality added to User model
    # Similar to the posts one-to-many relationship, we're using the so.relationship function to define the relationship in the model class
    # This relationship links User instances to other User instances, so as a convention let's say that for a pair of users linked by this relationship, the left side user is following the right side user
    # defining the relationship as seen from the left side user with the name following because when I query this relationship from the left side I will get the list of users the left-side user is following
    following: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.follower_id == id),#primaryjoin indicates the condition that links the entity to the association table. In the following relationship, the user has to match the follower_id attribute of the association table.  In the following relationship, the user has to match the follower_id attribute
        secondaryjoin=(followers.c.followed_id == id),# secondaryjoin indicates the condition that links the association table to the user on the other side of the relationship
        back_populates='followers')
    
    # Conversely, the followers relationship starts from the right side and finds all the users that follow a given user.
    followers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.followed_id == id),# In the following relationship, the user has to match the followed_id column
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following')
    
    #  the five functions below are methods to query and change follower associations.
    #  It is always best to move the application logic away from view functions and into models or other auxiliary classes or modules, because that makes unit testing much easier.

    #function to add this user as a follower of another user
    def follow(self, user):
        #  use the is_following() supporting method to make sure the requested action will not result in duplication
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user):
        # using the is_following() supporting method to ensure that this user is currently following the other user, before removing them as a follower
        if self.is_following(user):
            self.following.remove(user)

    # function to check whether this user is already following another user
    def is_following(self, user):
        # performs a query on the following relationship to see if a given user is already included in it.
        # All write-only relationships have a select() method that constructs a query that returns all the elements in the relationship.
        # In this case I do not need to request all the elements, I'm just looking for a specific user, so I can restrict the query with a where() clause.
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None
    

    # methods return the follower counts for the user (ie the number of users this user is following). 
    def followers_count(self):
        # This requires a different type of query, in which the results are not returned, but just their count is.
        # The sa.select() clause for these queries specify the sa.func.count() function from SQLAlchemy, to indicate that I want to get the result of a function.
        # The select_from() clause is then added with the query that needs to be counted.
        # Whenever a query is included as part of a larger query, SQLAlchemy requires the inner query to be converted to a sub-query by calling the subquery() method.
        query = sa.select(sa.func.count()).select_from(self.followers.select().subquery())
        return db.session.scalar(query)
    
    def following_count(self):
        query = sa.select(sa.func.count()).select_from(self.following.select().subquery())
        return db.session.scalar(query)






# Creating a database model for posts to represent post blogs written by users
class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    # body contains the body of the post as a string
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(

        # configured timestamp to be indexed, which is useful if you want to efficiently retrieve posts in chronological order.
        index=True,

        # added a default argument, and passed a lambda function that returns the current time in the UTC timezone.
        # When you pass a function as a default, SQLAlchemy will set the field to the value returned by the function.
        # In general, you will want to work with UTC dates and times in a server application instead of the local time where you are located.
        # This ensures that you are using uniform timestamps regardless of where the users and the server are located.
        # These timestamps will be converted to the user's local time when they are displayed.
        default=lambda: datetime.now(timezone.utc)
        )
    

    user_id: so.Mapped[int] = so.mapped_column(

        # The user_id field was initialized as a foreign key to User.id, which means that it references values from the id column in the users table.
        sa.ForeignKey(User.id),
        
        # Since not all databases automatically create an index for foreign keys,
        # the index=True option is added explicitly, so that searches based on this column are optimized.
        index=True
    )

    # Similar to the 'posts field bring in the User class,
    # the Post class has an author field that is also initialized as a relationship.
    # These two attributes allow the application to access the connected user and post entries.
    # Notice that here, the argument is not provided as a string (User refers to the class model).
    # This is because the User class was already defined earlier in this python module
    author: so.Mapped[User] = so.relationship(
        back_populates='posts'
        )


    def __repr__(self):
        return '<Post {}>'.format(self.body)


# Configuring a user loader callback function, that can be called to load a user given the ID
# this is required because Flask-Login knows nothing about databases, it needs the application's help in loading a user
# The user loader is registered with Flask-Login with the @login.user_loader decorator.
@login.user_loader
def load_user(id):

    # The id that Flask-Login passes to the function as an argument is going to be a string,
    # so databases that use numeric IDs need to convert the string to integer as you see below.
    return db.session.get(User, int(id))