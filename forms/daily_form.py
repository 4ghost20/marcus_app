from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class DailyReflectionForm(FlaskForm):
    reflection = TextAreaField("Today's Reflection",validators=[DataRequired(message="Please enter your reflection."), Length(min=3)])
    
    submit = SubmitField("Save Reflection")