from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager


app = Flask(__name__)
app.secret_key = '^%^&$^T&*Y(*&*^&*^*(&&*$^4765876986764^&%&*%^%$&*^(*^*%*&^436'
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://springstudent:springstudent@localhost/phongkhamtunhan?charset=utf8mb4'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SQLALCHEMY_RECORD_QUERIES"] = True


db = SQLAlchemy(app=app)
login = LoginManager(app=app)
