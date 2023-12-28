from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin

app = Flask(__name__)
app.secret_key = '^%^&$^T&*Y(*&*^&*^*(&&*$^4765876986764^&%&*%^%$&*^(*^*%*&^436'
app.config["SQLALCHEMY_DATABASE_URI"] = (
        'mysql+pymysql://springstudent:springstudent@localhost/phongkhamtunhan?charset=utf8mb4')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SQLALCHEMY_RECORD_QUERIES"] = True

app.config['TWILIO_ACCOUNT_SID'] = 'ACe3829a5417371c7f1e17904b68f3f123'
app.config['TWILIO_AUTH_TOKEN'] = 'a094b61d17ea7458ff64739a35bc1411'

app.config['UPLOAD_FOLDER'] = 'uploads'

login_manager = LoginManager(app=app)

db = SQLAlchemy(app=app)
admin = Admin(app=app, name='QUẢN TRỊ DANH SÁCH KHÁM BỆNH', template_mode='bootstrap4')
