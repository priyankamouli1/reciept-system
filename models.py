from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    preparation_steps = db.Column(db.Text, nullable=False)
    cooking_time = db.Column(db.Integer, nullable=False)
    serving_size = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(250), nullable=True)
    category = db.Column(db.String(255),nullable=False)
    author = db.Column(db.String(255),nullable=False,default="gowri")

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review = db.Column(db.Text,nullable=False)
    username = db.Column(db.String(255),nullable=False)
    recipe_id = db.Column(db.Integer,nullable=False)
    user_id = db.Column(db.Integer,nullable=False)
    rating = db.Column(db.Integer,nullable=False)