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


# class to represent users stored in the database
# The class inherits from db.Model, a base class for all models from Flask-SQLAlchemy.
# The User model defines several fields as class variables.
# These are the columns that will be created in the corresponding database table.
class User(db.Model):

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
