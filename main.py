from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import json
import ast


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

class UpdateForm(FlaskForm):
    rating = StringField('Your Rating Out of 10 expample 7.5', validators=[DataRequired()])
    your_review = StringField('Your Review', validators=[DataRequired()])
    submit = SubmitField('Done')

class AddMovie(FlaskForm):
    movie_title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')



# creating data base
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///my-top-movies.db"
# #Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# # creating table
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String, nullable=False)
    img_url = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Book {self.title}>'

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()

    db_lenght = len(db.session.query(Movie).all())
    return render_template("index.html",db_lenght=db_lenght,data=all_movies)

@app.route("/edit",methods=["GET","POST"])
def update():
    if request.args.get('data'):
        db_lenght = len(db.session.query(Movie).all())
        print(db_lenght)
        given_data = request.args.get('data')
        given_data = ast.literal_eval(given_data)
        li = list(given_data["release_date"].split("-"))
        year = li[0]
        movie_name=given_data["original_title"]

    else:
        movie_id = request.args.get('id')
        movie_to_update = Movie.query.get(movie_id)
        movie_name = movie_to_update.title

    form = UpdateForm()
    if form.validate_on_submit():
        if request.args.get('data'):
            new_movie = Movie(
                title=given_data["original_title"],
                year=year,
                description=given_data['overview'],
                rating=form.rating.data,
                review=form.your_review.data,
                ranking=1,
                img_url=given_data["poster_path"]
            )
            db.session.add(new_movie)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            movie_id = request.args.get('id')
            movie_to_update = Movie.query.get(movie_id)
            movie_to_update.rating = form.rating.data
            movie_to_update.review = form.your_review.data
            db.session.commit()
            return redirect(url_for('home'))
    return render_template("edit.html",form=form,name=movie_name)

@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    book_to_delete = Movie.query.get(movie_id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/add",methods=["GET","POST"])
def add():
    form = AddMovie()
    if form.validate_on_submit():
        query = {"api_key": "f3160cb2b7b1c093f106c2440dccb04d",
                 "query": f"{form.movie_title.data}"}

        response = requests.get("https://api.themoviedb.org/3/search/movie", params=query).json()["results"]
        data_lenght = len(response)
        print(data_lenght)

        movie_list = []
        for i in response:
            movie_list.append(i['original_title'])
        print(movie_list)
        return render_template("select.html",lenght_of_data=int(data_lenght),movie_data=response)
    return render_template("add.html",form=form)




if __name__ == '__main__':
    app.run(debug=True)
