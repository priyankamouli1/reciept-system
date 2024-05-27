from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask import Flask, render_template, redirect, url_for, request, flash,jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from werkzeug.security import generate_password_hash, check_password_hash
import os
from models import db, User,Recipe,Review
import re
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["SECRET_KEY"] = "gowri-shankar12"
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'db.sqlite')
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

login_manager = LoginManager()
login_manager.init_app(app)

engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
Session = sessionmaker(bind=engine)

db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/update_recipe', methods=['POST'])
def update_recipe():
    data = request.form
    recipe_id = data.get('recipe_id')
    recipe = Recipe.query.get(recipe_id)
    if recipe:
        recipe.title = data['title']
        recipe.ingredients = data['ingredients']
        recipe.category = data['category']
        recipe.preparation_steps = data['preparation_steps']
        recipe.cooking_time = data['cookingTime']
        recipe.serving_size = data['servingsize']
        recipe.description = data['description']
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image = Image.open(file)
                resized_image = image.resize((500, 375))
                resized_image.save(file_path)
                image_path = recipe.image_url
                if os.path.exists(image_path):
                    os.remove(image_path)
                recipe.image_url = file_path
        db.session.commit()
        return jsonify({'message': 'Recipe updated successfully'})
    
    return jsonify({'error': 'Recipe not found'}), 404


@app.route('/get_recipe/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if recipe:
        return jsonify({
            'id': recipe.id,
            'name': recipe.title,
            'description': recipe.description,
            'ingredients':recipe.ingredients,
            'preparation_steps':recipe.preparation_steps,
            'cookingTime':recipe.cooking_time,
            'servingsize':recipe.serving_size,
            'category':recipe.category,
            'image':recipe.image_url
        })
    else:
        return jsonify({'error': 'Recipe not found'}), 404

@app.route("/create_recipe", methods=['POST','GET'])
def create_recipe():
    if request.method=='GET':
        return render_template("create_recipe.html")
    author = current_user.username
    title = request.form['title']
    ingredients = request.form['ingredients']
    category = request.form['category']
    description = request.form['description']
    cookingTime = request.form['cookingTime']
    servingsize = request.form['servingsize']
    file = request.files['image']
    preparation_steps = request.form['preparation_steps']
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image = Image.open(file)
    resized_image = image.resize((500, 375))
    resized_image.save(file_path)
    #flash('Recipe successfully created!')
    new_recipe = Recipe(
        title=title,
        description=description,
        ingredients=ingredients,
        preparation_steps=preparation_steps,
        cooking_time=cookingTime,
        serving_size=servingsize,
        image_url=file_path,
        category=category
    )
    db.session.add(new_recipe)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/submit_review/<int:recipe_id>", methods=['POST'])
def post_review(recipe_id):
    if request.method == 'POST':
        review = request.form['review']
        username = current_user.username
        rating = request.form['rating']
        recipe_id = recipe_id
        user_id = current_user.id    
        new_review = Review(review=review, username=username, rating=rating, recipe_id=recipe_id, user_id=user_id)
        db.session.add(new_review)
        db.session.commit()
        ratings = db.session.query(
            Review.recipe_id,
            func.avg(Review.rating).label('average_rating')
        ).group_by(Review.recipe_id).all()
        rating_dict = {rating.recipe_id: rating.average_rating for rating in ratings}
        return redirect(url_for('recipe_detail', recipe_id=recipe_id,rating_dict=rating_dict))

@app.route("/recipes/<int:recipe_id>")
def recipe_detail(recipe_id):
    reviews = Review.query.filter_by(recipe_id=recipe_id).all()
    recipe = Recipe.query.get(recipe_id)
    ratings = db.session.query(
            Review.recipe_id,
            func.avg(Review.rating).label('average_rating')
        ).group_by(Review.recipe_id).all()
    rating_dict = {rating.recipe_id: rating.average_rating for rating in ratings}
    if not recipe:
        return "Recipe not found", 404
    preparation_steps = re.split(r'\b\d+\.\s*', recipe.preparation_steps)
    preparation_steps = [step for step in preparation_steps if step]
    return render_template("recipe_detail.html", recipe=recipe,preparation_steps=preparation_steps,reviews=reviews,rating_dict=rating_dict)

@app.route('/filter', methods=['GET', 'POST'])
def filter():
    if request.method == 'POST':
        category = request.form.get('category')
        ingredients = request.form.get('ingredients')
        cooking_time_range = request.form.get('cookingTime')
        filters = []
        if category:
            filters.append(Recipe.category==category)
        if ingredients:
            filters.append(Recipe.ingredients.like(f'%{ingredients}%'))
        if cooking_time_range:
            if cooking_time_range == '40->':
                filters.append(Recipe.cooking_time > 40)
            else:
                min_time, max_time = map(int, cooking_time_range.split('-'))
                filters.append(Recipe.cooking_time.between(min_time, max_time))
        recipes = Recipe.query.filter(*filters).all()
        ratings = db.session.query(
            Review.recipe_id,
            func.avg(Review.rating).label('average_rating')
        ).group_by(Review.recipe_id).all()
        rating_dict = {rating.recipe_id: rating.average_rating for rating in ratings}
        return render_template("home.html", recipes=recipes,rating_dict=rating_dict)
    else:
        return render_template('home.html')

@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        searchInput = request.form.get('searchInput')
        recipes = Recipe.query.filter(Recipe.title.like(f'%{searchInput}%')).all()
        ratings = db.session.query(
            Review.recipe_id,
            func.avg(Review.rating).label('average_rating')
        ).group_by(Review.recipe_id).all()
        rating_dict = {rating.recipe_id: rating.average_rating for rating in ratings}
        return render_template("home.html", recipes=recipes,rating_dict=rating_dict)
    return render_template("home.html")

@login_manager.user_loader
def load_user(user_id):
    session = Session()
    user = session.query(User).get(user_id)
    session.close()
    return user


@app.route("/delete_recipe/<int:recipe_id>", methods=["POST"])
def delete(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    image_path = recipe.image_url
    db.session.delete(recipe)
    db.session.commit()
    if os.path.exists(image_path):
        os.remove(image_path)
    #flash("Recipe has been deleted successfully.", "success")
    return redirect(url_for("home"))

@app.route("/")
def home():
    if current_user.is_authenticated:
        recipes = Recipe.query.all()
        ratings = db.session.query(
            Review.recipe_id,
            func.avg(Review.rating).label('average_rating')
        ).group_by(Review.recipe_id).all()
        rating_dict = {rating.recipe_id: rating.average_rating for rating in ratings}
        return render_template("home.html", recipes=recipes, rating_dict=rating_dict)
    else:
        return redirect(url_for('login'))

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.")
            return redirect(url_for("register"))
        if existing_email:
            flash("Email already exists. Please choose a different one.")
            return redirect(url_for("register"))
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, email=email)
        db.session.add(new_user)
        db.session.commit()
        flash("User Registered successfully")
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))
        login_user(user)
        return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/recipe")
def view_recipe():
    user_recipes = Recipe.query.filter(Recipe.author.like(f'%{current_user.username}%')).all()
    ratings = db.session.query(
            Review.recipe_id,
            func.avg(Review.rating).label('average_rating')
        ).group_by(Review.recipe_id).all()
    rating_dict = {rating.recipe_id: rating.average_rating for rating in ratings}
    return render_template("view_recipes.html",user_recipes=user_recipes,rating_dict=rating_dict)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0")