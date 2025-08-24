from app import db, bcrypt
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    token_expiration = db.Column(db.DateTime, nullable=True)
    products = db.relationship('Product', back_populates='owner', lazy=True)

    def __init__(self, username, email, password):
        self.username = username 
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)        

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"



        