# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import date, datetime, timedelta
from flask_migrate import Migrate
from forms.daily_form import DailyReflectionForm
from database import db
from models import User, Habit, DailyEntry, HabitCompletion

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marcus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "supersecretkey123"

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()


# ------------------- AUTH -------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user."""
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Prevent duplicate username or email
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


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login existing user."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Logged in")
            return redirect(url_for("dashboard"))
        else:
            flash("Incorrect username or password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Logout user and clear session."""
    session.clear()
    flash("Logged out")
    return redirect(url_for("login"))


# ------------------- HABIT HELPERS -------------------
def get_week_dates(anchor=None):
    """Return Mon–Sun dates for the week containing the anchor date."""
    anchor = anchor or date.today()
    start = anchor - timedelta(days=anchor.weekday())  # Monday start
    return [start + timedelta(days=i) for i in range(7)]


def is_planned_on(habit, d):
    """Check if a habit is scheduled for the given date (based on mon–sun flags)."""
    flags = [habit.mon, habit.tue, habit.wed, habit.thu, habit.fri, habit.sat, habit.sun]
    return flags[d.weekday()]


def completion_map(user_id, habits, week_days):
    """Return {habit_id: {date: completed_bool}} for the given week."""
    result = {h.id: {d: False for d in week_days} for h in habits}
    comps = HabitCompletion.query.filter(
        HabitCompletion.user_id == user_id,
        HabitCompletion.date.between(week_days[0], week_days[-1])
    ).all()
    for c in comps:
        if c.habit_id in result:
            result[c.habit_id][c.date] = bool(c.completed)
    return result


# ------------------- DASHBOARD -------------------
@app.route("/dashboard")
def dashboard():
    """Main dashboard showing counts and average weekly progress."""
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]

    reflections_count = DailyEntry.query.filter_by(user_id=user_id).count()
    habits_count = Habit.query.filter_by(user_id=user_id).count()

    # Weekly progress across all habits (Mon–Sun of current week)
    week_days = get_week_dates()
    habits = Habit.query.filter_by(user_id=user_id).all()
    comp_map = completion_map(user_id, habits, week_days)
    total_planned = sum(1 for h in habits for d in week_days if is_planned_on(h, d))
    total_done = sum(1 for h in habits for d in week_days if is_planned_on(h, d) and comp_map[h.id][d])
    weekly_progress = round((total_done / total_planned * 100), 1) if total_planned > 0 else 0

    return render_template(
        "dashboard.html",
        username=session["username"],
        reflections_count=reflections_count,
        habits_count=habits_count,
        weekly_progress=weekly_progress
    )


# ------------------- STATIC PAGES -------------------
@app.route('/')
def home():
    return render_template('home.html', username="zen", message="stay steady today.")

@app.route('/about')
def about():
    today = date.today().strftime("%B %d, %Y")
    return render_template('about.html', today=today)


# ------------------- DAILY REFLECTIONS -------------------
@app.route('/daily', methods=['GET', 'POST'])
def daily():
    """Create a daily reflection."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    form = DailyReflectionForm()
    virtue = "Discipline"
    virtues_list = ["Kindness", "Patience", "Courage", "Honesty", "Gratitude"]

    if form.validate_on_submit():
        entry = DailyEntry(
            title=form.title.data,
            content=form.content.data,
            user_id=session["user_id"]
        )
        db.session.add(entry)
        db.session.commit()
        flash("Reflection saved!", "success")
        return redirect(url_for("entries"))

    return render_template("daily.html", form=form, virtue=virtue, virtues_list=virtues_list)


@app.route('/entries')
def entries():
    """View all reflections for the logged-in user, with optional search."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    q = request.args.get("q", "")
    if q:
        entries = DailyEntry.query.filter(
            DailyEntry.user_id == session["user_id"],
            (DailyEntry.title.ilike(f"%{q}%")) | (DailyEntry.content.ilike(f"%{q}%"))
        ).order_by(DailyEntry.created_at.desc()).all()
    else:
        entries = DailyEntry.query.filter_by(
            user_id=session["user_id"]
        ).order_by(DailyEntry.created_at.desc()).all()

    return render_template("all_entries.html", entries=entries)


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_reflection(id):
    """Edit an existing reflection."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    entry = DailyEntry.query.get_or_404(id)
    if entry.user_id != session.get("user_id"):
        flash("Access denied")
        return redirect(url_for("entries"))

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


@app.route("/delete/<int:id>", methods=["POST"])
def delete_reflection(id):
    """Delete a reflection."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    entry = DailyEntry.query.get_or_404(id)
    if entry.user_id != session.get("user_id"):
        flash("Access denied")
        return redirect(url_for("entries"))

    db.session.delete(entry)
    db.session.commit()
    flash("Reflection deleted.", "danger")
    return redirect(url_for("entries"))


# ------------------- HABITS: LIST / CREATE / DELETE -------------------
@app.route("/habits", methods=["GET", "POST"])
def habits():
    """List habits and create new ones with weekday flags."""
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]

    if request.method == "POST":
        habit_name = request.form.get("habit_name")
        days = request.form.getlist("days")  # e.g., ["mon", "tue", ...]
        if habit_name:
            new_habit = Habit(
                user_id=user_id,
                name=habit_name,
                mon="mon" in days, tue="tue" in days, wed="wed" in days,
                thu="thu" in days, fri="fri" in days, sat="sat" in days, sun="sun" in days
            )
            db.session.add(new_habit)
            db.session.commit()
            flash("Habit added!", "success")

    habits = Habit.query.filter_by(user_id=user_id).all()
    return render_template("habits.html", habits=habits)


@app.route("/habits/delete/<int:habit_id>", methods=["POST"])
def delete_habit(habit_id):
    """Delete a habit owned by the logged-in user."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id != session["user_id"]:
        flash("Access denied", "danger")
        return redirect(url_for("habits"))

    db.session.delete(habit)
    db.session.commit()
    flash("Habit deleted.", "info")
    return redirect(url_for("habits"))


# ------------------- HABITS: WEEKLY VIEW + COMPLETION -------------------
@app.route("/habits/weekly")
def habits_weekly():
    """Weekly grid displaying planned habits and completion status."""
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]

    # Optional query param: anchor date (YYYY-MM-DD) to view a specific week
    anchor_str = request.args.get("date")
    try:
        anchor = datetime.strptime(anchor_str, "%Y-%m-%d").date() if anchor_str else date.today()
    except ValueError:
        anchor = date.today()

    week_days = get_week_dates(anchor)
    habits = Habit.query.filter_by(user_id=user_id).order_by(Habit.name.asc()).all()
    if not habits:
        flash("No habits yet. Add one first!", "info")
        return redirect(url_for("habits"))

    comp_map = completion_map(user_id, habits, week_days)

    # Build rows for the template and compute per-habit progress
    rows, progress = [], {}
    for h in habits:
        days = [{"date": d, "planned": is_planned_on(h, d), "completed": comp_map[h.id][d]} for d in week_days]
        rows.append({"habit": h, "days": days})
        total_planned = sum(cell["planned"] for cell in days)
        total_done = sum(cell["planned"] and cell["completed"] for cell in days)
        progress[h.id] = round((total_done / total_planned * 100), 1) if total_planned else 0

    return render_template("habits_weekly.html", week_days=week_days, rows=rows, progress=progress, anchor=anchor)


@app.route("/habits/complete", methods=["POST"])
def toggle_habit_completion():
    """Toggle or set completion for a habit on a specific date."""
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user_id = session["user_id"]

    habit_id = request.form.get("habit_id", type=int)
    date_str = request.form.get("date")
    completed_flag = request.form.get("completed")  # "true"/"false" or None

    if not habit_id or not date_str:
        return jsonify({"error": "Missing habit_id or date"}), 400

    habit = Habit.query.get(habit_id)
    if not habit or habit.user_id != user_id:
        return jsonify({"error": "Not found or forbidden"}), 404

    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date"}), 400

    # Only allow completion toggles on planned days
    if not is_planned_on(habit, d):
        return jsonify({"error": "Habit not planned for this day"}), 400

    comp = HabitCompletion.query.filter_by(habit_id=habit_id, user_id=user_id, date=d).first()
    if comp:
        comp.completed = completed_flag.lower() == "true" if completed_flag else not comp.completed
    else:
        comp = HabitCompletion(
            habit_id=habit_id, user_id=user_id, date=d,
            completed=True if completed_flag is None else (completed_flag.lower() == "true")
        )
        db.session.add(comp)

    db.session.commit()
    return jsonify({"ok": True, "habit_id": habit_id, "date": d.isoformat(), "completed": comp.completed})


# ------------------- LESSONS -------------------
@app.route('/lessons')
def lessons():
    return render_template("lessons.html")


# ------------------- MAIN -------------------
if __name__ == "__main__":
    app.run(debug=True)
