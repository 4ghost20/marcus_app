# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date
from flask_migrate import Migrate
from forms.daily_form import DailyReflectionForm  # make sure class name matches
from models import db, User, Reflection, Habit, Note, DailyEntry

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marcus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "supersecretkey123"

# Initialize db and migrations
db.init_app(app)
migrate = Migrate(app, db)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# ------------------- ROUTES -------------------

@app.route('/')
def home():
    return render_template('home.html',
        username="zen",
        message="stay steady today.")

@app.route('/about')
def about():
    today = date.today().strftime("%B %d, %Y")
    return render_template('about.html', today=today)

@app.route('/daily', methods=['GET', 'POST'])
def daily():
    form = DailyReflectionForm()
    virtue = "Discipline"
    virtues_list = ["Kindness", "Patience", "Courage", "Honesty", "Gratitude"]

    if form.validate_on_submit():
        # Save entry to DB
        new_entry = DailyEntry(title=form.title.data, content=form.content.data)
        db.session.add(new_entry)
        db.session.commit()

        flash("Reflection saved successfully!", "success")
        return redirect(url_for('daily'))

    return render_template("daily.html",
                           form=form,
                           virtue=virtue,
                           virtues_list=virtues_list)

@app.route('/entry', methods=['GET', 'POST'])
def entry():
    form = DailyReflectionForm()
    if form.validate_on_submit():
        new_entry = DailyEntry(title=form.title.data, content=form.content.data)
        db.session.add(new_entry)
        db.session.commit()

        preview = (form.content.data[:120] + '...') if len(form.content.data) > 120 else form.content.data
        flash(f"Reflection received: \"{preview}\"", "success")
        return redirect(url_for('entry'))

    return render_template('entry.html', form=form)

@app.route('/lessons')
def lessons():
    return render_template("lessons.html")

@app.route('/entries')
def entries():
    # Display all daily entries
    entries = DailyEntry.query.order_by(DailyEntry.created_at.desc()).all()
    return render_template('all_entries.html', entries=entries)

# ------------------- MAIN -------------------

if __name__ == "__main__":
    app.run(debug=True)
