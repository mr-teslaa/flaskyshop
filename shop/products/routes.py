import os
import secrets
from PIL import Image
from flask import redirect
from flask import render_template
from flask import url_for
from flask import flash
from flask import request

from shop import app
from shop import db
from shop.products.models import Brands
from shop.products.models import Categories
from shop.products.models import AddProduct
from shop.products.forms import AddBrandForm
from shop.products.forms import AddCategoryForm
from shop.products.forms import AddProducts

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)

    output_size = (1080, 1080)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route('/addbrand', methods=['GET', 'POST'])
def addbrand():
    form = AddBrandForm()
    if form.validate_on_submit():
        brand = Brands(name=form.brand_name.data)
        db.session.add(brand)
        db.session.commit()
        flash(f'Brand {form.brand_name.data} has been successfully added', 'success')
        return redirect(url_for('addbrand'))
    return render_template('products/addBrandCategory.html', form=form, title='Add Brand', brands='brands')


@app.route('/addcategory', methods=['GET', 'POST'])
def addcategory():
    form = AddCategoryForm()
    if form.validate_on_submit():
        category = Categories(name=form.category_name.data)
        db.session.add(category)
        db.session.commit()
        flash(f'Category {form.category_name.data} has been successfully added', 'success')
        return redirect(url_for('addcategory'))
    return render_template('products/addBrandCategory.html', form=form, title='Add Brand')

@app.route('/addproduct', methods=['GET', 'POST'])
def addproduct():
    brands = Brands.query.all()
    categories = Categories.query.all()
    form = AddProducts()
    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data
        discount = form.discount.data
        stock = form.stock.data
        description = form.description.data
        colors = form.name.data
        description = form.description.data
        brand = request.form.get('brand')
        category = request.form.get('category')

        if form.image1.data:
            product_image1 = save_picture(form.image1.data)
            addproduct = AddProduct(name=name, price=price, discount=discount, stock=stock, colors=colors,
                    desc=description, category_id=category, brand_id=brand, image1=product_image1)
        elif form.image1.data and form.image2.data:
            product_image1 = save_picture(form.image1.data)
            product_image2 = save_picture(form.image2.data)
            addproduct = AddProduct(name=name, price=price, discount=discount, stock=stock, colors=colors,
                    desc=description, category_id=category, brand_id=brand, image1=product_image1, image2=product_image2)
        elif form.image1.data and form.image3.data:
            product_image1 = save_picture(form.image1.data)
            product_image3 = save_picture(form.image3.data)
            addproduct = AddProduct(name=name, price=price, discount=discount, stock=stock, colors=colors,
                    desc=description, category_id=category, brand_id=brand, image1=product_image1, image3=product_image3)
        elif form.image1.data and form.image2.data and form.image3.data:
            product_image1 = save_picture(form.image1.data)
            product_image2 = save_picture(form.image2.data)
            product_image3 = save_picture(form.image3.data)
            addproduct = AddProduct(name=name, price=price, discount=discount, stock=stock, colors=colors,
                    desc=description, category_id=category, brand_id=brand, image1=product_image1, image2=product_image2, image3=product_image3)
        flash(f'Product {name} has been successfully added', 'success')
        db.session.add(addproduct)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template(
        'products/addProducts.html', form=form, title='Add Products',
        brands=brands, categories=categories)