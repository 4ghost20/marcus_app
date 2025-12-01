from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date 
from forms.daily_form import DailyReflectionForm

app = Flask(__name__)

app.config['SECRET_KEY'] = "supersecretkey123"
@app.route('/')
def home():
    return render_template('home.html',
        username="zen",
        message="stay steady today.")

@app.route('/about')
def about():
    today = date.today().strftime("%B %d, %Y")
    return render_template('about.html',today=today)


@app.route('/daily',  methods=['GET', 'POST'])
def daily():
    form = DailyReflectionForm()
    reflection_text = None

    if form.validate_on_submit():
        reflection_text = form.reflection.data

    virtue = "Discipline"
    virtues_list = ["Kindness", "Patience", "Courage", "Honesty", "Gratitude"]

    return render_template("daily.html", form=form, reflection=reflection_text, virtue=virtue, virtues_list=virtues_list)

@app.route('/lessons')
def lessons():
    return render_template("lessons.html")

@app.route('/entry', methods=['GET', 'POST'])
def entry():
    form = DailyReflectionForm()
    if form.validate_on_submit():               # POST + valid
        reflection_text = form.reflection.data

        # Print to console for developer visibility (what you requested)
        print("New reflection submitted:", reflection_text)
        app.logger.info("New reflection submitted: %s", reflection_text)

        # Friendly confirmation for the user (short preview)
        preview = (reflection_text[:120] + '...') if len(reflection_text) > 120 else reflection_text
        flash(f"Reflection received: \"{preview}\"", "success")

        # POST-Redirect-GET prevents duplicate form submissions on refresh
        return redirect(url_for('entry'))

    # GET or invalid POST → show the form (errors will appear automatically)
    return render_template('entry.html', form=form)

if __name__ == "__main__":
    app.run(debug=True)
