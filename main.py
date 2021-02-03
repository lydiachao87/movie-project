
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, HiddenField
from wtforms.validators import DataRequired, Length
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///favorite_movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db= SQLAlchemy(app)

API_KEY = os.environ['API_KEY']
SEARCH_API_ENDPOINT ="https://api.themoviedb.org/3/search/movie"
MOVIE_INFO_ENDPOINT ="https://api.themoviedb.org/3/movie"

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(100), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

class SearchMovie(FlaskForm):
    title = StringField(label="Movie Title", validators=[DataRequired()])
    submit = SubmitField(label="Add Movie")

class MovieUpdate(FlaskForm):
    id = HiddenField(label="id")
    rating = FloatField(label="Your Rating Out of 10 e.g. 7.5", validators=[DataRequired()])
    review = StringField(label="Your Review", validators=[DataRequired(), Length(max=100)])
    submit = SubmitField(label="Done")


# db.create_all()

# movie_pic_url ="https://static.wikia.nocookie.net/beautyandthebeast2017/images/c/cd/BATB-1991.jpg/revision/latest?cb=20170319022717"
# new_movie = Movie(title="Beauty and the Beast", year=1991, description="A prince cursed to spend his days as a hideous monster sets out to regain his humanity by earning a young woman's love.", rating=8.0, ranking=1, review="One of my all-time favourite movies!", img_url=movie_pic_url)
# db.session.add(new_movie)
# db.session.commit()

@app.route("/")
def home():
    order_of_movies = Movie.query.order_by(Movie.rating.asc()).all()
    num_of_movies = len(order_of_movies)
    for movie in order_of_movies:
        movie.ranking = num_of_movies
        num_of_movies -= 1
    db.session.commit()
    # all_movies = db.session.query(Movie).all()
    return render_template("index.html", movies=order_of_movies)

@app.route('/add', methods=('GET', 'POST'))
def add():
    movie = SearchMovie()

    if request.method == "POST":
        title = request.form['title']

        parameters = {
            "api_key": API_KEY,
            "query": title,
        }
        search_response = requests.get(SEARCH_API_ENDPOINT, params=parameters)
        results = search_response.json()['results']

        return render_template('select.html', movie=results)

    return render_template('add.html', form=movie)

@app.route('/update', methods=('GET', 'POST'))
def update():
    movie_id = request.args.get('id', type=int)
    movie_selected = Movie.query.get(movie_id)
    movie_update_form = MovieUpdate()

    if request.method=="POST":
        movie_id = request.args.get('id')
        movie_to_update = Movie.query.get(movie_id)
        movie_to_update.rating = request.form['rating']
        movie_to_update.review = request.form['review']
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('edit.html', update=movie_update_form, movie=movie_selected )

@app.route('/delete')
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/select', methods=('GET','POST'))
def select_film():
    movie_id = int(request.args.get('id'))
    # print(movie_id)
    movie_params={
        "movie_id": movie_id,
        "api_key": API_KEY,
    }
    selected_movie_endpoint = f"{MOVIE_INFO_ENDPOINT}/{movie_id}"
    # print(selected_movie_endpoint)
    movie_response = requests.get(selected_movie_endpoint, params=movie_params)
    movie_detail_results = movie_response.json()
    title = movie_detail_results['original_title']
    # print(title)
    release_date = movie_detail_results['release_date']
    year = int(release_date.split("-")[0])
    # print(year)
    description = movie_detail_results['overview']
    # print(description)
    rating = 0
    ranking = 0
    review = "None"
    url_start = "https://www.themoviedb.org/t/p/w600_and_h900_bestv2"
    poster_path = movie_detail_results['poster_path']
    img_url = url_start + poster_path
    # print(img_url)
    new_movie = Movie(title=title, year=year, description=description, rating=rating, ranking=ranking, review=review, img_url=img_url)
    db.session.add(new_movie)
    db.session.commit()
    # movie_to_update = Movie.query.filter_by(title=title).first()
    # id = movie_to_update.id
    return redirect(url_for('update', id=new_movie.id))



if __name__ == '__main__':
    app.run(debug=True)
