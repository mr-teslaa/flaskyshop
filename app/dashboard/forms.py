from flask_wtf import FlaskForm

from wtforms import StringField
from wtforms import PasswordField
from wtforms import IntegerField
from wtforms import SubmitField
from wtforms import BooleanField
from wtforms import TextAreaField
from wtforms import SelectField

from flask_wtf.file import FileField
from flask_wtf.file import FileAllowed

from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Email
from wtforms.validators import EqualTo
from wtforms.validators import ValidationError

from app.models import Users

class RegistrationForm(FlaskForm):
    username = StringField(
        'Username',
        validators = [
            DataRequired(),
            Length(min=2, max=20)
        ]
    )

    phone = StringField(
        'Phone',
        validators=[
            DataRequired(),
            Length(min=1, max=11)
        ]
    )

    email = StringField(
        'Email',
        validators = [
            DataRequired(),
            Email()
        ]
    )

    password = PasswordField(
        'Password',
        validators = [ DataRequired() ]
    )

    confirm_password = PasswordField(
        'Confirm Password',
        validators = [
            DataRequired(),
            EqualTo('password')
        ]
    )

    submit = SubmitField('Sign Up')
    
    def validate_phone(self, phone):
        user_phone = Users.query.filter_by(email=phone.data).first()
        if user_phone:
            raise ValidationError('This Phone is alredy registerd. Please choose a different one.')

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user_email = Users.query.filter_by(email=email.data).first()
        if user_email:
            raise ValidationError('That email is taken. Please choose a different one.')
            


class LoginForm(FlaskForm):
    phone = StringField(
        'Phone',
        validators=[
            DataRequired(),
            Length(min=1, max=11)
        ]
    )

    password = PasswordField(
        'Password', 
        validators = [DataRequired()]
    )

    remember = BooleanField('Remember Me')

    submit = SubmitField('Login')

# ADD BRAND FORM
class AddBrandForm(FlaskForm):
    brand_name = StringField(
        'Brand Name',
        validators=[DataRequired()]
    )

    brand_logo = FileField(
            'Brand Logo',
            validators = [
                FileAllowed(['jpg', 'png', 'webp', 'jpeg'])
            ]
    )

    brand_note = TextAreaField('Note (Optional)')
    
    submit = SubmitField('Save')

# ADD CATEGORY FORM
class AddCategoryForm(FlaskForm):
    category_name = StringField(
        'Category Name',
        validators=[DataRequired()]
    )

    category_note = TextAreaField('Note (Optional)')
    
    submit = SubmitField('Save')

# ADD PRODUCT FORM
class AddProductForm(FlaskForm):
    product_name = StringField(
        'Product Name',
        validators=[DataRequired()]
    )

    product_id = StringField(
        'Product ID',
        validators=[DataRequired()]
    )

    product_price = IntegerField(
        'Product Price',
        validators=[DataRequired()]
    )

    product_quantity = IntegerField(
        'Product Quantity',
        validators=[DataRequired()]
    )

    product_description = TextAreaField('Product Description')
    
    product_brand = SelectField(
        'Product Brand', 
        choices=[],
        validators=[DataRequired()]
    )

    product_category = SelectField(
        'Product Category', 
        choices=[],
        validators=[DataRequired()]
    )

    product_available = SelectField(
        'Is this product available?',
        choices=[
            ('yes', 'Yes' ),
            ('no', 'No' )
        ],
        validators=[DataRequired()] 
    ) 

    product_image = FileField(
            'Product Image',
            validators = [
                FileAllowed(['jpg', 'png', 'webp', 'jpeg'])
            ]
    )

    submit = SubmitField('Save')


# EDIT PRODUCT FORM
class EditProductForm(FlaskForm):
    product_name = StringField(
        'Product Name'
    )

    product_id = StringField(
        'Product ID'
    )

    product_price = IntegerField(
        'Product Price'
    )

    product_quantity = IntegerField(
        'Product Quantity'
    )

    product_description = TextAreaField('Product Description')
    
    product_brand = SelectField(
        'Product Brand', 
        choices=[]
    )

    product_category = SelectField(
        'Product Category', 
        choices=[]
    )

    product_available = SelectField(
        'Is this product available?',
        choices=[
            ('yes', 'Yes' ),
            ('no', 'No' )
        ],
        validators=[DataRequired()] 
    ) 

    product_image = FileField(
            'Upload New Image',
            validators = [
                FileAllowed(['jpg', 'png', 'webp', 'jpeg'])
            ]
    )

    submit = SubmitField('Save')


# ADD CUSTOMER FORM
class AddCustomerForm(FlaskForm):
    customer_name = StringField(
        'Customer Name',
        validators=[DataRequired()]
    )

    customer_contact_number = StringField(
        'Customer Contact Number', 
        validators=[
            DataRequired(),
            Length(min=1, max=11)
        ]
    )

    customer_address = TextAreaField('Customer Address')
    
    submit = SubmitField('Save')

# ADD TODAY SELL FORM
class AddTodaySellForm(FlaskForm):
    customer_name = SelectField(
        'Customer Name', 
        choices=[],
        validators=[DataRequired()]
    )

    product_name = SelectField(
        'Product Name', 
        choices=[],
        validators=[DataRequired()]
    )

    quantity = IntegerField(
        'Quantity', 
        validators=[DataRequired()]
    )

    discount = IntegerField(
        'Discount (in taka)', 
        validators=[DataRequired()]
    )

    price = IntegerField(
        'Price', 
        validators=[DataRequired()]
    )

    payment_status = SelectField(
        'Payment Status',
        choices = [
            ('cash', 'Cash' ),
            ('card', 'Card' ),
            ('online(bkash/nagad)', 'Online (bKash/Nagad)' )
        ],
        validators = [
            DataRequired()
        ]
    )

    trnx_id = StringField('Transaction ID (optional)')

    note = TextAreaField('Note (Optional)')