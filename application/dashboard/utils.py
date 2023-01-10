#   importing necessary module
import os
import uuid
import secrets
import datetime
from PIL import Image
from flask import url_for
from flask import current_app
# from flask_mail import Message
# from flaskblog import mail


#   GENERATING INVOICE NUMBER
def invoiceID():
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    return timestamp + str(uuid.uuid4().int)[:6]


#   saving logo
def save_logo(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/brandlogo', picture_fn)

    output_size = (300, 300)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

#   saving profile picture
def save_profile_picture(form_picture):
    random_hex = secrets.token_hex(6)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_picture', picture_fn)

    output_size = (300, 300)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

#   SAVE PRODUCT IMAGE
def save_product(form_picture):
    random_hex = secrets.token_hex(22)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/productimages', picture_fn)

    output_size = (300, 500)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


# #   sending email
# def send_reset_email(user):
#     token = user.get_reset_token()
#     msg = Message('Password Reset Request',
#                   sender='noreply@demo.com',
#                   recipients=[user.email])
#     msg.body = f'''To reset your password, visit the following link:
# {url_for('users.reset_token', token=token, _external=True)}
# If you did not make this request then simply ignore this email and no changes will be made.
# '''
#     mail.send(msg)