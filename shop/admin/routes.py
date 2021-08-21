import os
from flask import render_template
from flask import session
from flask import request
from flask import url_for
from flask import redirect
from flask import flash

from shop import app
from shop import db
from shop import bcrypt
from shop.admin.forms import RegistrationForm
from shop.admin.forms import LoginForm
from shop.admin.models import User

@app.route('/')
def index():
    return render_template('index.html', title='Home')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        user = User(
                username=form.username.data,
                email=form.email.data,
                password=hash_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Salam {form.username.data}. Your account has been created!', 'success')
        return redirect(url_for('index'))
    return render_template('admin/register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['email'] = form.email.data
            flash(f'{form.email.data}, you have successfully logged in!', 'success')
            return redirect(request.args.get('next') or url_for('index'))
        else:
            flash(f'Wrong credentials, try again', 'danger')
    return render_template('admin/login.html', form=form, title='Login')