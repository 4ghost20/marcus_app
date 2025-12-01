# models.py
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    reflections = db.relationship('Reflection', backref='user', lazy=True)
    habits = db.relationship('Habit', backref='user', lazy=True)
    notes = db.relationship('Note', backref='user', lazy=True)

class Reflection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day_number = db.Column(db.Integer)
    content = db.Column(db.Text, nullable=False)

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    frequency = db.Column(db.String(50))
    completed = db.Column(db.Boolean, default=False)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150))
    content = db.Column(db.Text)
