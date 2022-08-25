#   importing basic flask module
from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import flash
from flask import current_app

#   importing module from flask login
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from app import db
from app.models import Users
# from app.admin.forms import LoginForm

admin = Blueprint('admin', __name__)

@admin.route('/')
def index():
    return render_template('admin/index.html')

@admin.route('/login/')
def admin_login():
    return render_template('admin/login.html', title="Admin Login")

@admin.route('/admin/dashboard/')
def dashboard():
    return render_template('admin/dashboard.html', title='Dashboard')

@admin.route('/admin/products/')
def products():
    return render_template('admin/products.html', title='Products')