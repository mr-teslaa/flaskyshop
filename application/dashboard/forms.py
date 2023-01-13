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

from flask_login import current_user
from application.models import Users
from application.models import Products

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
        user_phone = Users.query.filter_by(phone=phone.data).first()
        print(f"User Found: {user_phone}")
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




# UPDATE PROFILE FORM
class UpdateProfileForm(FlaskForm):

    username = StringField(
        'Username',
        validators = [ 
            Length(min=2, max=20)
        ]
    )

    email = StringField(
        'Email',
        validators = [
            Email()
        ]
    )

    phone = StringField(
        'Phone',
        validators=[
            DataRequired(),
            Length(min=1, max=11)
        ]
    )

    picture = FileField(
        'Update Profile Picture', 
        validators = [
            FileAllowed(['jpg','jpeg','png'])
        ]
    )

    current_password = PasswordField(
        'Current Password'
    )

    new_password = PasswordField(
        'New Password'
    )

    confirm_password = PasswordField(
        'Confirm New Password'
    )

    submit = SubmitField('Save')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = Users.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = Users.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')




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
        'Selling Price',
        validators=[DataRequired()]
    )

    product_buying_price = StringField(
        'Buying Price', 
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

    def validate_product_id(self, product_id):
        print("=============== start finding product ============")
        if product_id.data:
            print(f"Product Found: {product_id.data}")
            product = Products.query.filter_by(productid=product_id.data).first()
            print(f"Product Found: {product}")
            if product:
                raise ValidationError('Product already added.')


# EDIT PRODUCT FORM
class EditProductForm(FlaskForm):
    product_name = StringField(
        'Product Name',
        validators=[DataRequired()] 
    )

    product_id = StringField(
        'Product ID',
        validators=[
            DataRequired(),
            Length(min=1)
        ] 
    )

    product_price = IntegerField(
        'Product Price',
        validators=[DataRequired()] 
    )

    product_buying_price = StringField(
        'Buying Price',
        validators=[DataRequired()] 
    )

    product_quantity = IntegerField(
        'Product Quantity',
        validators=[DataRequired()] 
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

    def validate_product_id(self, product_id):
        current_produdct_id = product_id.data.strip()
        if current_produdct_id:
            product = Products.query.filter_by(productid=current_produdct_id).first()
            if str(product.productid) != str(current_produdct_id):
                raise ValidationError('Product already added.')


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
        'Discount (in taka)'
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
            ('bkash/nagad', 'bKash/Nagad' ),
            ('pending', 'Pending')
        ],
        validators = [
            DataRequired()
        ]
    )

    trnx_id = StringField('Transaction ID (optional)')

    note = TextAreaField('Note (Optional)')

    submit = SubmitField('Confirm')