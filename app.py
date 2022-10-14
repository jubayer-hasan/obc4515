import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'database.db')

app.permanent_session_lifetime = timedelta(minutes=30)

db = SQLAlchemy(app)
import views
