from flask import Flask, render_template
from datetime import date 

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('home.html',
        username="zen",
        message="stay steady today.")

@app.route('/about')
def about():
    today = date.today().strftime("%B %d, %Y")
    return render_template('about.html',today=today)


@app.route('/daily')
def daily():
    virtue = "Discipline"
    virtues_list = ["Kindness", "Patience", "Courage", "Honesty", "Gratitude"]

    return render_template('daily.html', virtue=virtue, virtues_list=virtues_list)

if __name__ == "__main__":
    app.run(debug=True)
