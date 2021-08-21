from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import IntegerField
from wtforms import PasswordField
from wtforms import TextAreaField
from wtforms import SubmitField
from wtforms import BooleanField
from flask_wtf.file import FileField
from flask_wtf.file import FileAllowed
from flask_wtf.file import FileRequired
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Email
from wtforms.validators import EqualTo
from wtforms.validators import ValidationError

class AddProducts(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    discount = IntegerField('Discount', default=0)
    stock = IntegerField('Stock', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    colors = TextAreaField('Colors', validators=[DataRequired()])

    image1 = FileField(
        'Image 1',
        validators = [
            FileRequired(),
            FileAllowed(['jpg','png', 'gif', 'jpeg'])
        ]
    )

    image2 = FileField(
        'Image 2',
        validators = [
            FileAllowed( ['jpg','png', 'gif', 'jpeg'] )
        ]
    )

    image3 = FileField(
        'Image 3',
        validators = [
            FileAllowed( ['jpg','png', 'gif', 'jpeg'] )
        ]
    )

    submit = SubmitField('Add')

class AddBrandForm(FlaskForm):
    brand_name = StringField( 'Add Brand', validators=[ DataRequired() ] )
    submit = SubmitField('Add')

class AddCategoryForm(FlaskForm):
    category_name = StringField( 'Add Category', validators=[ DataRequired() ] )
    submit = SubmitField('Add')