from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField
from wtforms import SubmitField
from wtforms.validators import DataRequired



class ProductForm(FlaskForm):
    title = StringField('Навание', validators=[DataRequired()])
    category = SelectField('Категория товара', choices=[(1, 'Вымышленный'), (2, 'Вооброжаемый')], validators=[DataRequired()])
    price = IntegerField('Цена')
    description = TextAreaField("Описание")
    submit = SubmitField('Добавить')