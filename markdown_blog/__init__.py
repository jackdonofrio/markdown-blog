from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mde import Mde
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)
# app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SECRET_KEY'] = 'TEMPORARY_DELETE_BEFORE_DEPLOYMENT'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
mde = Mde(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from markdown_blog import routes
