from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class CommentForm(FlaskForm):
    context = TextAreaField('Текст комментария', validators=[DataRequired()])
    submit = SubmitField('Оставить комментарий')