from flask import redirect
from flask import request
from flask import url_for
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

class AccessAdminPanel(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role=='admin' 

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('users.user_login', next=request.url))