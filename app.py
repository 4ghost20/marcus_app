# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import date
from flask_migrate import Migrate
from forms.daily_form import DailyReflectionForm
from models import db, DailyEntry
from models import User
from database import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marcus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "supersecretkey123"

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

# ------------------- REGISTER -------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Check duplication
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("User already exists")
            return redirect(url_for("register"))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Account created. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


# ------------------- LOGIN -------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Logged in")
            return redirect(url_for("dashboard"))

        flash("Incorrect username or password")

    return render_template("login.html")


# ------------------- LOGOUT -------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out")
    return redirect(url_for("login"))


# ------------------- DASHBOARD -------------------
@app.route("/")
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["username"])

# ------------------- ROUTES -------------------

@app.route('/')
def home():
    return render_template('home.html',
        username="zen",
        message="stay steady today."
    )


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
        entry = DailyEntry(title=form.title.data, content=form.content.data)
        db.session.add(entry)
        db.session.commit()
        flash("Reflection saved!", "success")
        return redirect(url_for("entries"))

    return render_template("daily.html",
                           form=form,
                           virtue=virtue,
                           virtues_list=virtues_list)


# View all reflections
@app.route('/entries')
def entries():
    q = request.args.get("q", "")
    if q:
        entries = DailyEntry.query.filter(
            DailyEntry.title.ilike(f"%{q}%") |
            DailyEntry.content.ilike(f"%{q}%")
        ).order_by(DailyEntry.created_at.desc()).all()
    else:
        entries = DailyEntry.query.order_by(DailyEntry.created_at.desc()).all()

    return render_template("all_entries.html", entries=entries)


# Edit reflection
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_reflection(id):
    entry = DailyEntry.query.get_or_404(id)
    form = DailyReflectionForm()

    if form.validate_on_submit():
        entry.title = form.title.data
        entry.content = form.content.data
        db.session.commit()
        flash("Reflection updated!", "success")
        return redirect(url_for("entries"))

    form.title.data = entry.title
    form.content.data = entry.content

    return render_template("edit.html", form=form, entry=entry)


# Delete reflection
@app.route("/delete/<int:id>", methods=["POST"])
def delete_reflection(id):
    entry = DailyEntry.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    flash("Reflection deleted.", "danger")
    return redirect(url_for("entries"))

@app.route('/lessons')
def lessons():
    return render_template("lessons.html")



# ------------------- MAIN -------------------
if __name__ == "__main__":
    app.run(debug=True)
