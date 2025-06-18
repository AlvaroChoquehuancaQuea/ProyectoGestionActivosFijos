from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from database import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(128))  # Este campo almacena la contraseña hasheada

    def __init__(self, name, email, username, password):
        self.name = name
        self.email = email
        self.username = username
        self.password_hash = self.hash_password(password)

    def hash_password(self, password):
        return generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)
  
    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_by_id(user_id):
       return User.query.get(user_id)