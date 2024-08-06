
from flask import Flask,render_template,request,redirect,url_for,flash
import pickle
from flask_bootstrap import Bootstrap
import numpy as np
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length , ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user , current_user , logout_user , login_required,LoginManager,UserMixin
from flask_sqlalchemy import SQLAlchemy 
import threading
from time import sleep
from flask_apscheduler import APScheduler
from sklearn.metrics.pairwise import cosine_similarity
import warnings
import pandas as pd
import joblib



books = joblib.load('books.pkl')
ratings = joblib.load('ratings.pkl')

app = Flask(__name__)
app.app_context().push()
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///UserdataDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
scheduler = APScheduler()
# scheduler.init_app(app)



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])

    def validate_username(self , username):
        user = User123.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That Username is taken. Please choose a new one')

@login_manager.user_loader
def load_user(user_id):
    return User123.query.get(int(user_id))


class User123( db.Model , UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique = True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))


@app.route('/')
def index():
    popular_df = joblib.load('popbooks.pkl')
    return render_template('index.html',
                           isbn = list(popular_df['ISBN'].values),
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )

@app.route('/recommend')
@login_required
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books',methods=['post'])
@login_required
def recommend():
    pt = joblib.load('pt.pkl')
    similarity_scores = joblib.load('similarity_scores.pkl')
    user_input = request.form.get('user_input')
    if user_input == "":
        flash(f"Please type something in the search-box before submitting!!!" , 'danger')
        return render_template('recommend.html')
    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(item)

    return render_template('recommend.html',data=data)

#login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    next_url = request.form.get("next")
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if form.validate_on_submit():
        user = User123.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user , remember = form.remember.data )
                # next_page = request.args.get("next")
                # print(next_page)
                flash(f"Welcome {form.username.data}! , You have successfully logged in to our website." , 'success')
                if next_url:
                    return redirect(next_url)
                return redirect(url_for("index"))
        flash("You have given wrong username or password , please try again." , "danger")
        return redirect(url_for('login'))

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if form.validate_on_submit():
        users = joblib.load('users.pkl')
        hashed_password = generate_password_hash(form.password.data)
        new_user = User123(username=form.username.data, email=form.email.data, password=hashed_password,user_id = (users.shape[0]+1))
        db.session.add(new_user)
        db.session.commit()
        print(request.form.get('location'))
        print(request.form.get('age'))
        df = {'User-ID':(users.shape[0]+1) , 'Location': request.form.get('location'), 'Age': float(request.form.get('age'))}
        # users = users.append(df, ignore_index = True)
        df = pd.DataFrame([df])
        users = pd.concat([users, df], ignore_index=True)
        joblib.dump(users, 'users.pkl')
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

    
@app.route("/detail")
@login_required
def detail():
    isbn = request.args.get('isbn')
    ratings = request.args.get('rating')
    votes = request.args.get('numvotes')
    book123 = books[books['ISBN'] == isbn]
    ratingsdf = joblib.load('ratings.pkl')
    numb = ratingsdf.loc[(ratingsdf['User-ID'] == int(current_user.user_id)) & (ratingsdf['ISBN'] == isbn)]
    upd = "noupdate"
    if len(numb) > 0:
        upd = "update"
    return render_template("detail.html" , isbn = isbn , ratings = ratings , votes = votes , booktitle = book123['Book-Title'].values[0] , author = book123['Book-Author'].values[0] , year = book123['Year-Of-Publication'].values[0] , publisher = book123['Publisher'].values[0] , image = book123['Image-URL-L'].values[0] , upd = upd)


@app.route("/aboutus")
def aboutus():
    return render_template("about.html")


@app.route("/star")
def star():
    isbn = request.args.get('isbn1')
    ratings = request.args.get('ratings1')
    votes = request.args.get('votes1')
    up = request.args.get('up1')
    print(up)
    return render_template("star.html" , isbn = isbn , ratings = ratings , votes = votes , up = up)

@app.route("/starss" , methods = ['get' , 'post'])
def starss():
    sleep(2)
    ratingsdf = joblib.load('ratings.pkl')
    isbn = request.args.get('isbn2')
    ratings = request.args.get('ratings2')
    votes = request.args.get('votes2')
    up = request.args.get('up2')
    user_rating = request.form.get('rate')
    if up == "yes":
        ind = ratingsdf.loc[(ratingsdf['User-ID'] == int(current_user.user_id)) & (ratingsdf['ISBN'] == isbn)].index[0]
        ratingsdf.loc[ ind ,'Book-Rating'] = float(user_rating)
        print(ratingsdf)
    else:
        ratingsdf.loc[len(ratingsdf)] = [int(current_user.user_id) , isbn , float(user_rating) ]
        print(ratingsdf)
    joblib.dump(ratingsdf, 'ratings.pkl')
    return redirect(url_for('detail' , isbn = isbn , rating = ratings , numvotes = votes))

def data_update(): 
    print("started updation")
    # For the updation of the top 50 popular books
    ratings = joblib.load('ratings.pkl')
    ratings_with_name = ratings.merge(books,on='ISBN')
    num_rating_df = ratings_with_name.groupby('Book-Title').count()['Book-Rating'].reset_index()
    num_rating_df.rename(columns={'Book-Rating':'num_ratings'},inplace=True)
    warnings.filterwarnings("ignore" , category=FutureWarning)
    avg_rating_df = ratings_with_name.groupby('Book-Title').mean()['Book-Rating'].reset_index()
    avg_rating_df.rename(columns={'Book-Rating':'avg_rating'},inplace=True)
    popular_df = num_rating_df.merge(avg_rating_df,on='Book-Title')
    popular_df = popular_df[popular_df['num_ratings']>=250].sort_values('avg_rating',ascending=False).head(50)
    popular_df = popular_df.merge(books,on='Book-Title').drop_duplicates('Book-Title')[['ISBN','Book-Title','Book-Author','Image-URL-M','num_ratings','avg_rating']]
    joblib.dump(popular_df, 'popbooks.pkl')
    # For recommending using collaborative Filtering
    x = ratings_with_name.groupby('User-ID').count()['Book-Rating'] > 200
    padhe_likhe_users = x[x].index
    filtered_rating = ratings_with_name[ratings_with_name['User-ID'].isin(padhe_likhe_users)]
    y = filtered_rating.groupby('Book-Title').count()['Book-Rating']>=50
    famous_books = y[y].index
    final_ratings = filtered_rating[filtered_rating['Book-Title'].isin(famous_books)]
    pt = final_ratings.pivot_table(index='Book-Title',columns='User-ID',values='Book-Rating')
    pt.fillna(0,inplace=True)
    similarity_scores = cosine_similarity(pt)
    joblib.dump(pt, 'pt.pkl')
    joblib.dump(similarity_scores, 'similarity_scores.pkl')
    print("updation is done ")



if __name__ == '__main__':
    #This is how we use a schedular , with the help of which we can run some code in the background in a completely different thread
    # Instead of APschedular we can also use the threading module of python to create a seperate thread and do the same but there also remember to prevent debug= true as told below to avaoid relaoding and all , its example is shown below
    # t = threading.Thread(target=print_rahul)
    # t.start()
    # scheduler.add_job(func=data_update, trigger='interval',id='interval-task-id', seconds = 30 )
    # scheduler.start()
    # Remember that If you write here debug = true then the APschedular will run the "print_rahul" function twice as by default what flask does is it runs the application as well as again run the application in 1 or 2 second for debugging purpose so below what we do is set reloading to false
    app.run(host="0.0.0.0",port=5000,debug=True)
    # app.run(debug=True)