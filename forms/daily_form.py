# forms/daily_form.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class DailyReflectionForm(FlaskForm):  # renamed to match import
    title = StringField("Title")
    content = TextAreaField("Reflection", validators=[DataRequired()])
    submit = SubmitField("Save Entry")
