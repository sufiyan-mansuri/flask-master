from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError
from wtforms.fields import FileField 
from flask_wtf.file import FileAllowed, FileRequired
from app.models.user import User

PRODUCT_CATEGORIES = [
    ('electronics', 'Electronics'),
    ('clothing', 'Clothing'),
    ('books', 'Books')
]

class ProductForm(FlaskForm):
    class Meta: 
        csrf = False

    name = StringField('name', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('description', validators=[Length(max=500)])
    price = FloatField('price', validators=[DataRequired()])
    category = SelectField('category', choices=PRODUCT_CATEGORIES, validators=[DataRequired()])
    is_available = BooleanField('is_available')
    image = FileField('product_image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images Only!')])

    def validate_price(self, field):
        if field.data <= 0:
            raise ValidationError('Price must be a positive number.')