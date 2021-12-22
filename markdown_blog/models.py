from markdown_blog import db, login_manager
from datetime import datetime
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    joindate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    bio = db.Column(db.String(100), nullable=False, default="A blogger")
    articles = db.relationship('Article', backref='author', lazy=True)

    def user_image(self):
        """ 
        just gonna use identicons, because of uniqueness + 
        not dealing with potential file saving / uploading issues
        """

        return f"https://api.kwelo.com/v1/media/identicon/{self.username}"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False, default='Untitled Article')
    html_content = db.Column(db.Text, nullable=False)
    raw = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)