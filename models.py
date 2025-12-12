from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Relationships
    reflections = db.relationship('DailyEntry', backref='user', lazy=True)
    habits = db.relationship('Habit', backref='user', lazy=True)
    notes = db.relationship('Note', backref='user', lazy=True)

    # New: access to habit completions through backref
    habit_completions = db.relationship('HabitCompletion', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

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

    def __repr__(self):
        return f"<DailyEntry {self.id} {self.title or ''}>"

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", name="fk_habit_user_id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500))
    frequency = db.Column(db.String(50))  # 'daily', 'weekly', etc.
    start_date = db.Column(db.Date, default=date.today)

    # This 'completed' flag can represent overall completion or today's status,
    # but detailed tracking will be handled by HabitCompletion.
    completed = db.Column(db.Boolean, default=False)

    # 7-day template as booleans (which days the habit is planned)
    mon = db.Column(db.Boolean, default=False)
    tue = db.Column(db.Boolean, default=False)
    wed = db.Column(db.Boolean, default=False)
    thu = db.Column(db.Boolean, default=False)
    fri = db.Column(db.Boolean, default=False)
    sat = db.Column(db.Boolean, default=False)
    sun = db.Column(db.Boolean, default=False)

    # New: relationship to completions
    completions = db.relationship('HabitCompletion', backref='habit', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Habit {self.name}>"

class HabitCompletion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(
        db.Integer,
        db.ForeignKey('habit.id', name='fk_habitcompletion_habit_id'),
        nullable=False,
        index=True
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', name='fk_habitcompletion_user_id'),
        nullable=False,
        index=True
    )
    date = db.Column(db.Date, nullable=False, index=True, default=date.today)
    completed = db.Column(db.Boolean, default=True, nullable=False)

    # Optional: ensure one record per habit per date per user
    __table_args__ = (
        db.UniqueConstraint('habit_id', 'user_id', 'date', name='uq_habit_user_date'),
    )

    def __repr__(self):
        return f"<HabitCompletion habit={self.habit_id} user={self.user_id} date={self.date} completed={self.completed}>"

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150))
    content = db.Column(db.Text)

    def __repr__(self):
        return f"<Note {self.id} {self.title or ''}>"
