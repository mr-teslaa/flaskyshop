from shop import db
from datetime import datetime


class AddProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Numeric(10,2), nullable=False)
    discount = db.Column(db.Integer, default=0)
    stock = db.Column(db.Integer, nullable=False)
    colors = db.Column(db.Text, nullable=False)
    desc = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    brand = db.relationship('Brands', backref=db.backref('brands', lazy=True))

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    brand = db.relationship('Categories', backref=db.backref('categories', lazy=True))

    image1 = db.Column(db.String(150), nullable=False, default='image.jpeg')
    image2 = db.Column(db.String(150), default='image.jpeg')
    image3 = db.Column(db.String(150), default='image.jpeg')

    def __repr__(self):
        return f"Addproduct('{self.name}')"

class Brands(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)

    def __repr__(self):
        return f"Brands('{self.name}')"

class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)

    def __repr__(self):
        return f"Categories('{self.name}')"