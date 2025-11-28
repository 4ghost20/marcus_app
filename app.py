from flask import Flask, render_template, request
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

if __name__ == "__main__":
    app.run(debug=True)
