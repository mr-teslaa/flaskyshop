#   importing basic flask module
from email.mime import image
from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import flash
from flask import abort
from flask import current_app

#   importing module from flask login
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from app import db
from app import bcrypt

from app.models import Brands
from app.models import Categories
from app.models import Products
from app.models import Users
from app.models import Customers

from app.dashboard.forms import LoginForm 
from app.dashboard.forms import RegistrationForm
from app.dashboard.forms import AddCustomerForm
from app.dashboard.forms import AddBrandForm
from app.dashboard.forms import AddCategoryForm 
from app.dashboard.forms import AddProductForm
from app.dashboard.forms import AddTodaySellForm

#   CUSTOM MODULE
from app.dashboard.utils import save_logo
from app.dashboard.utils import save_product

dashboard = Blueprint('dashboard', __name__)

# LANDING PAGE
@dashboard.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.admin_dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Users(phone=form.phone.data, username=form.username.data, email=form.email.data, password=hashed_password, user_role='admin')
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in ✅', 'success')
        return redirect(url_for('dashboard.admin_login'))

    return render_template('public/register.html', form=form)


#   ADMIN LOGIN
@dashboard.route('/login/', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('users.user_dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(phone=form.phone.data).first()
        # if user and bcrypt.check_password_hash(user.password, form.password.data) and user.user_role == 'admin':
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login success ✅', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.admin_dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password ⚠️', 'danger')
    return render_template('public/login.html', title="Admin Login", form=form)


#   ADMIN LOGOUT
@dashboard.route("/logout/")
@login_required
def user_logout():
    logout_user()
    return redirect(url_for('dashboard.admin_login'))


#   ADMIN DASHBOARD
@dashboard.route('/dashboard/')
# @login_required
def admin_dashboard():
    return render_template('dashboard/dashboard.html', title='Dashboard')


#   DAILY SELL
@dashboard.route('/dashboard/todaysell/', methods=['GET', 'POST'])
# @login_required
def todaysell():
    form=AddTodaySellForm()
    form.customer_name.choices = [(customer.id, customer.customer_name) for customer in Customers.query.all()]
    return render_template('dashboard/todaysell.html', title='Today\'s Sell', form=form)


#   BRAND
@dashboard.route('/dashboard/brand/', methods=['GET', 'POST'])
# @login_required
def brand():
    #   FETCHING EXISTING BRAND
    brands = Brands.query.all()
    total_brand = Brands.query.paginate()

    #   ADDING NEW BRAND
    form = AddBrandForm()
    if form.validate_on_submit():
        if form.brand_logo.data:
            picture_file = save_logo(form.brand_logo.data)
            brand_logo = url_for('static', filename='brandlogo/' + picture_file)
            brand = Brands(name=form.brand_name.data, logo=brand_logo, note=form.brand_note.data)
        else:
            brand = Brands(name=form.brand_name.data, note=form.brand_note.data)
        db.session.add(brand)
        db.session.commit()
        flash(f'Brand "{form.brand_name.data}" added successfully ✅', 'success')
        return redirect(url_for('dashboard.brand'))
    return render_template('dashboard/brand.html', title='Brand', form=form, brands=brands, total_brand=total_brand)


#   EDIT BRAND
@dashboard.route("/dashboard/brand/<int:brand_id>/update/", methods=['GET', 'POST'])
# @login_required
def edit_brand(brand_id):
    brand = Brands.query.get_or_404(brand_id)
    form = AddBrandForm()
    if form.validate_on_submit():
        if form.brand_logo.data:
            brand.name = form.brand_name.data
            picture_file = save_logo(form.brand_logo.data)
            brandlogo = url_for('static', filename='brandlogo/' + picture_file)
            brand.logo = brandlogo
            brand.note = form.brand_note.data
            db.session.commit()
            flash('Brand details has been updated ✅', 'success')
        else:
            brand.name = form.brand_name.data
            brand.note = form.brand_note.data
            db.session.commit()
            flash('Brand details has been updated ✅', 'success')
        return redirect(url_for('dashboard.brand', brand_id=brand.id))
    elif request.method == 'GET':
        form.brand_name.data = brand.name
        form.brand_logo.data = brand.logo
        form.brand_note.data = brand.note
    return render_template('dashboard/brand_edit.html', form=form, brand=brand)


#   DELETE BRAND
@dashboard.route("/dashboard/brand/<int:brand_id>/delete/", methods=['POST'])
# @login_required
def delete_brand(brand_id):
    brand = Brands.query.get_or_404(brand_id)
    db.session.delete(brand)
    db.session.commit()
    flash(f'Brand "{brand.name}" has been deleted ✅', 'success')
    return redirect(url_for('dashboard.brand'))


#   CATEGORY
@dashboard.route('/dashboard/category/', methods=['GET', 'POST'])
# @login_required
def category():
    #   FETCHING EXISTING CATEGORY
    categories = Categories.query.all()
    total_category = Categories.query.paginate()

    #   ADDING NEW CATEGORY
    form = AddCategoryForm()
    if form.validate_on_submit():
        category = Categories(name=form.category_name.data, note=form.category_note.data)
        db.session.add(category)
        db.session.commit()
        flash(f'Category "{form.category_name.data}" added successfully ✅', 'success')
        return redirect(url_for('dashboard.category'))
    return render_template('dashboard/category.html', title='Category', form=form, categories=categories, total_category=total_category)


#   EDIT CATEGORY
@dashboard.route("/dashboard/category/<int:category_id>/update/", methods=['GET', 'POST'])
# @login_required
def edit_category(category_id):
    category = Categories.query.get_or_404(category_id)
    form = AddCategoryForm()
    if form.validate_on_submit():
        category.name = form.category_name.data
        category.note = form.category_note.data
        db.session.commit()
        flash('Category details has been updated ✅', 'success')
        return redirect(url_for('dashboard.category', category_id=category.id))
    elif request.method == 'GET':
        form.category_name.data = category.name
        form.category_note.data = category.note
    return render_template('dashboard/category_edit.html', form=form, category=category)


#   DELETE CATEGORY
@dashboard.route("/dashboard/category/<int:category_id>/delete/", methods=['POST'])
# @login_required
def delete_category(category_id):
    category = Categories.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash(f'Category "{category.name}" Deleted ✅', 'success')
    return redirect(url_for('dashboard.category'))


#   PRODUCTS
@dashboard.route('/dashboard/products/', methods=['GET', 'POST'])
# @login_required
def products():
    form=AddProductForm()
    form.product_brand.choices = [(brand.id, brand.name) for brand in Brands.query.all()]
    form.product_category.choices = [(category.id, category.name) for category in Categories.query.all()]
    
    #   fetch existing product
    existingproduct = Products.query.all()

    if form.validate_on_submit():
        productname = form.product_name.data
        productID = form.product_id.data
        productprice = form.product_price.data
        productquantity = form.product_quantity.data
        # if existingproduct:
        #     productquantity = form.product_quantity.data + existingproduct.stock
        # else:
        #     productquantity = form.product_quantity.data
        productdescription = form.product_description.data
        productbrand = form.product_brand.data
        productcategory = form.product_category.data
        productimage = form.product_image.data

        if productimage:
            picture_file = save_product(productimage)
            imagefile = url_for('static', filename='productimages/' + picture_file)
            product = Products(name=productname, productid=productID, price=productprice, 
                                stock=productquantity, description= productdescription, brand_id=productbrand, 
                                category_id= productcategory, image1=imagefile)  
            # STORING IN DB
            db.session.add(product)
            db.session.commit()
            return redirect(url_for('dashboard.products'))    

        product = Products(name=productname, productid=productID, price=productprice, 
                            stock=productquantity, description= productdescription,  brand= productbrand, 
                            category= productcategory)
        # STORING IN DB
        db.session.add(product)
        db.session.commit()

        return redirect(url_for('dashboard.products'))

    return render_template('dashboard/products.html', title='Products', form=form, existingproduct=existingproduct)


#   EDIT PRODUCTS
@dashboard.route("/dashboard/product/<int:product_id>/update/", methods=['GET', 'POST'])
# @login_required
def edit_product(product_id):
    product = Products.query.get_or_404(product_id)
    form = AddProductForm()
    if form.validate_on_submit():
        productname = form.product_name.data
        productID = form.product_id.data
        productprice = form.product_price.data
        productquantity = form.product_quantity.data
        productdescription = form.product_description.data
        productbrand = form.product_brand.data
        productcategory = form.product_category.data
        productimage = form.product_image.data
        #   CHECK IF NEW IMAGE ADDED
        if productimage:
            picture_file = save_logo(productimage)
            productlogo = url_for('static', filename='productimages/' + picture_file)
            product.image1 = productlogo
        
        product.name = productname
        product.productid = productID
        product.price = productprice
        product.stock = productquantity
        product.description = productdescription
        product.brand.name = productbrand
        product.category = productcategory
        db.session.commit()
        flash('Product details has been updated ✅', 'success')
        return redirect(url_for('dashboard.products'))

    if request.method == 'GET':
        form.product_name.data = product.name
        form.product_id.data = product.productid
        form.product_price.data = product.price 
        form.product_quantity.data = product.stock 
        form.product_description.data = product.description 
        form.product_brand.choices = [(brand.id, brand.name) for brand in Brands.query.all()]
        form.product_category.choices = [(category.id, category.name) for category in Categories.query.all()] 
    return render_template('dashboard/product_edit.html', form=form, product=product)


#   ORDERS
@dashboard.route('/dashboard/orders/', methods=['GET', 'POST'])
# @login_required
def orders():
    return render_template('dashboard/orders.html', title='Orders')

#   CUSTOMER
@dashboard.route('/dashboard/customer/', methods=['GET', 'POST'])
# @login_required
def customer():
    #   FETCHING EXISTING CUSTOMER
    customers = Customers.query.all()
    total_customer = Customers.query.paginate()

    #   ADDING NEW CUSTOMER
    form = AddCustomerForm()
    if form.validate_on_submit():
        customer = Customers(customer_name=form.customer_name.data, customer_contact_number=form.customer_contact_number.data, customer_address=form.customer_address.data)
        db.session.add(customer)
        db.session.commit()
        flash(f'Customer "{form.customer_name.data}" added successfully ✅', 'success')
        return redirect(url_for('dashboard.customer'))
    return render_template('dashboard/customer.html', title='Customer', form=form, customers=customers, total_customer=total_customer)


#   EDIT CUSTOMER
@dashboard.route("/dashboard/customer/<int:customer_id>/update/", methods=['GET', 'POST'])
# @login_required
def edit_customer(customer_id):
    customer = Customers.query.get_or_404(customer_id)
    form = AddCustomerForm()
    if form.validate_on_submit():
        customer.customer_name = form.customer_name.data
        customer.customer_contact_number = form.customer_contact_number.data
        customer.customer_address = form.customer_address.data
        db.session.commit()
        flash('Customer details has been updated ✅', 'success')
        return redirect(url_for('dashboard.customer', customer_id=customer.id))
    elif request.method == 'GET':
        form.customer_name.data = customer.customer_name
        form.customer_contact_number.data = customer.customer_contact_number
        form.customer_address.data = customer.customer_address
    return render_template('dashboard/customer_edit.html', form=form)


#   DELETE CUSTOMER
@dashboard.route("/dashboard/customer/<int:customer_id>/delete/", methods=['POST'])
# @login_required
def delete_customer(customer_id):
    customer = Customers.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    flash(f'Customer "{customer.customer_name}" Deleted ✅', 'success')
    return redirect(url_for('dashboard.customer'))


#   REPORT
@dashboard.route('/dashboard/report/', methods=['GET', 'POST'])
# @login_required
def report():
    return render_template('dashboard/report.html', title='Report')