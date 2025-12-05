from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    reflections = db.relationship('DailyEntry', backref='user', lazy=True)
    habits = db.relationship('Habit', backref='user', lazy=True)
    notes = db.relationship('Note', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class DailyEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Only one user_id, with a named FK
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', name='fk_dailyentry_user_id'),
        nullable=False
    )
class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", name="fk_habit_user_id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500))
    frequency = db.Column(db.String(50))  # 'daily', 'weekly', etc.
    start_date = db.Column(db.Date, default=date.today)
    completed = db.Column(db.Boolean, default=False)

    # 7-day progress as booleans
    mon = db.Column(db.Boolean, default=False)
    tue = db.Column(db.Boolean, default=False)
    wed = db.Column(db.Boolean, default=False)
    thu = db.Column(db.Boolean, default=False)
    fri = db.Column(db.Boolean, default=False)
    sat = db.Column(db.Boolean, default=False)
    sun = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Habit {self.name}>"

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150))
    content = db.Column(db.Text)
