import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import string
import random



app = Flask(__name__)

################ SQL Alchemy Configuration ##################

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' +os.path.join(basedir, 'data.sqlite')
app.config['SOLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)

###############################################################

class URL(db.Model):
    __tablename__ = "urls"
    id = db.Column ("id",db.Integer, primary_key=True)
    long = db.Column ("long",db.String())
    short = db.Column ("short",db.String(3))
    def __init__(self, long, short):
        self.long = long
        self.short = short
 
    
        
    

@app.before_first_request
def create_tables():
    db.create_all()
    

def shorten_url():
    #letters = string.ascii_lowercase + string.ascii_uppercase
    letters = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
    while True:
        rand_letters = random.choices(letters,k=3)
        rand_letters = ''.join(rand_letters) #converting list to string
        short_url = URL.query.filter_by(short=rand_letters).first()
        if not short_url:
            return rand_letters

    
    

@app.route('/' , methods=["GET","POST"])
def index():
    if request.method == 'POST':
        url_received = request.form["long_url"]
        # check if url already exists in db
        found_url = URL.query.filter_by(long=url_received).first()
        if found_url:
            #return short url if found
            return redirect(url_for('display_short_url', url=found_url.short))
        else:
            #create short url if not found
            short_url = shorten_url()
            new_url = URL(url_received, short_url)
            db.session.add(new_url)
            db.session.commit()
            return redirect(url_for('display_short_url',url=short_url ))
    else:
        return render_template('home.html')

      
@app.route("/display/<url>")
def display_short_url(url):
    return render_template("shorturl.html", short_url_display=url)
  
 
@app.route("/<short_url>")
def redirection(short_url):
    long_url = URL.query.filter_by(short=short_url).first()
    if long_url:
        return redirect(long_url.long)
    else:
        return f'<h1>url dosent exists</h1>'

@app.route("/display")
def display():
    urls = URL.query.all()
    return render_template("display.html", urls=urls)


@app.route("/delete/<int:id>")
def delete(id):
    row = URL.query.get_or_404(id)
    db.session.delete(row)
    db.session.commit()
    return redirect("/display")


if __name__ == '__main__':
    app.run(debug=True)