#   importing  necessary module
from datetime import datetime
from flask import current_app

#   importing dataase
from app import db

#   importing login manager
from app import login_manager
from flask_login import UserMixin


#   making sure that the user is logged in
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    phone = db.Column(db.String(12), unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile = db.Column(db.String(), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    user_role = db.Column(db.String(60), default="user")
    join_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ip = db.Column(db.String(60))
    user_dailysells = db.relationship('DailySells', backref='user_dailysells', lazy=True)

class Brands(db.Model):
    __tablename__ = 'brands'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    logo = db.Column(db.String())
    note = db.Column(db.String())


class Categories(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    note = db.Column(db.String())

class Customers(db.Model, UserMixin):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(), nullable=False)
    customer_contact_number = db.Column(db.String())
    customer_address = db.Column(db.String())
    daily_sells = db.relationship('DailySells', backref=db.backref('daily_sells', lazy=True))

class Products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    productid = db.Column(db.String(), nullable=False)
    price = db.Column(db.String(), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default='00')
    colors = db.Column(db.Text())
    description = db.Column(db.Text())
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    available_status = db.Column(db.String(), default='yes')

    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    brand = db.relationship('Brands', backref=db.backref('product', lazy=True))
    
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    category = db.relationship('Categories', backref=db.backref('product', lazy=True))
    image1 = db.Column(db.String(), nullable=False, default='demoproduct.jpg')


class SelledProducts(db.Model):
    __tablename__ = 'selled_products'
    id = db.Column(db.Integer, primary_key=True)
    productname = db.Column(db.String())
    productid = db.Column(db.String())
    price = db.Column(db.String())
    quantity = db.Column(db.String())
    unittotal = db.Column(db.String())
    daily_sells_id = db.Column(db.Integer, db.ForeignKey('daily_sells.id'))
    

class DailySells(db.Model):
    __tablename__ = 'daily_sells'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)

    invoiceid = db.Column(db.String())
    selled_products = db.relationship('SelledProducts', backref=db.backref('selled_products', lazy=True))
    subtotal = db.Column(db.String())
    discount = db.Column(db.String())
    totalprice = db.Column(db.String())
    payment_status = db.Column(db.String(), default='cash')
    trnx_id = db.Column(db.String())
    note = db.Column(db.String())
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)