from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'b041ae62b36431840f94327319597e627aa37236ba7fae3521edeb0d8712f685'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "User needs to be logged in to view this page"
login_manager.login_message_category = "info"


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['TESTING'] = False
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEBUG'] = True
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_DEFAULT_SENDER'] = ''
app.config['MAIL_MAX_EMAILS'] = 1
app.config['MAIL_SUPRESS_SEND'] = False
app.config['MAIL_ASCII_ATTACHMENTS'] = False

mail = Mail(app)

from minor import route
