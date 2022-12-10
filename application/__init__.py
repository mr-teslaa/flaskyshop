from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_migrate import upgrade
from application.config import Config

from flask_admin import Admin
from application.admin import AccessAdminPanel

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()

login_manager.login_view = 'dashboard.admin_login'

login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    admin = Admin(app, name='BM Gatget & Technology', template_mode='bootstrap4')

    from application.models import Users
    from application.models import Customers
    from application.models import Products
    from application.models import Brands
    from application.models import Categories
    from application.models import SelledProducts
    from application.models import DailySells

    from application.dashboard.views import dashboard
    app.register_blueprint(dashboard)

    admin.add_view(AccessAdminPanel(Users, db.session))
    admin.add_view(AccessAdminPanel(Customers, db.session))
    admin.add_view(AccessAdminPanel(Products, db.session))
    admin.add_view(AccessAdminPanel(Brands, db.session))
    admin.add_view(AccessAdminPanel(Categories, db.session))
    admin.add_view(AccessAdminPanel(SelledProducts, db.session))
    admin.add_view(AccessAdminPanel(DailySells, db.session))

    return app