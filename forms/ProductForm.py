from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class ProductForm(FlaskForm):
    title = StringField('Навание', validators=[DataRequired()])
    price = IntegerField('Цена', validators=[DataRequired()])
    description = TextAreaField("Описание")
    submit = SubmitField('Добавить')