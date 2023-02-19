# ////////////////////////////////
# 0. API  
# 1. REALTIME SEARCH   
# 2. DASHBOARD
# ////////////////////////////////


import os
import json

from datetime import datetime

#   importing basic flask module
from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import flash
from flask import abort
from flask import jsonify
from flask import make_response
from flask import current_app

from datetime import datetime
from sqlalchemy import func
from sqlalchemy import extract
from sqlalchemy import and_

#   importing module from flask login
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from application import db
from application import bcrypt

from application.models import Brands
from application.models import Categories
from application.models import Products
from application.models import Users
from application.models import Customers
from application.models import DailySells
from application.models import SelledProducts

from application.dashboard.forms import LoginForm 
from application.dashboard.forms import RegistrationForm
from application.dashboard.forms import AddCustomerForm
from application.dashboard.forms import AddBrandForm
from application.dashboard.forms import AddCategoryForm 
from application.dashboard.forms import AddProductForm
from application.dashboard.forms import EditProductForm
from application.dashboard.forms import AddTodaySellForm 
from application.dashboard.forms import UpdateProfileForm 
from application.dashboard.forms import ReportForm

#   CUSTOM MODULE
from application.dashboard.utils import save_logo
from application.dashboard.utils import save_product 
from application.dashboard.utils import save_profile_picture 
from application.dashboard.utils import invoiceID

import barcode
from barcode.writer import ImageWriter
from io import BytesIO

# =================================================
# ===== START OF latest code for reportlab ========
# ================================================= 

# from reportlab.lib.pagesizes import A7
# from reportlab.lib.units import mm
# from reportlab.pdfgen import canvas

# from io import BytesIO
# from reportlab.lib.pagesizes import letter
# from reportlab.lib.units import inch
# from reportlab.pdfgen import canvas

# ================================================ 
# ===== END OF latest code for reportlab =========
# ================================================ 




dashboard = Blueprint('dashboard', __name__)

shopname = "BM GADGET & TECH"

# LANDING PAGE
@dashboard.route('/')
def index():
    return render_template('public/index.html')


#   ===========================
#   START API
#   ===========================

#   GET TODAY SELLS INFO
@dashboard.route('/api/todaysell/price/get/', methods=['POST'])
@login_required
def todaysell_price_get():
    today = datetime.utcnow().date()
    today_sells = DailySells.query.filter(DailySells.pub_date.like(f'{today}%')).all()

    # Get the total sell price and pending price for the current day
    sell_price, pending_price = 0, 0
    total_sell_product = 0
    today_profit = 0

    for sell in today_sells:

        # AS WE HAVE RELATION WITH SelledProducts TABLE
        # WE CAN ACCESS THEM AND PROCEED 
        for product in sell.selled_products:
            total_sell_product += 1

            # CHECK IF THE PAYMENT IS ACTUALLY PAID
            if sell.payment_status != 'pending':
                today_profit += product.calculate_profit()

        if sell.payment_status != 'pending':
            sell_price += int(sell.totalprice) 
        elif sell.payment_status == 'pending':
            pending_price += int(sell.totalprice)

    obj = {
        "message": "GET Sell Successfully",
        "selledtk": sell_price,
        "pendingtk": pending_price,
        "todaydate": today.strftime('%d %b, %Y'),
        "totalsellproduct": total_sell_product,
        "todayprofit": today_profit
    }
    res =  make_response(jsonify(obj), 200)
    return res


#   GET PRICE FOR A SINGLE PRODUCT
@dashboard.route('/api/newsell/<string:product_id>/price/get/', methods=['POST'])
@login_required
def product_price_get(product_id):
    getproduct = Products.query.filter_by(productid=product_id).first()
    
    if getproduct.stock < 1:
        getproduct.available_status = 'no'
        db.session.commit()

    if getproduct.available_status == 'yes':
        product = {
            "message": "Product Found",
            "name": getproduct.name,
            "price": getproduct.price,
            "productid": getproduct.productid,
            "stock": getproduct.stock
        }
    else:
        product = {
            "message": "Out of stock product",
            "name": getproduct.name,
            "price": "Out of stock",
            "productid": "Out of stock",
            "stock": getproduct.stock
        }
    res =  make_response(jsonify(product), 200)
    return res 


#   GET TOTAL SELL INFO
@dashboard.route('/api/allsell/info/get/', methods=['POST'])
@login_required
def allsell_info_get():
    allsell = DailySells.query.all()
    stock = Products.query.with_entities(func.sum(Products.stock)).scalar()
    sellprice, pendingprice = 0, 0
    totalselleproduct = SelledProducts.query.with_entities(func.sum(SelledProducts.quantity)).scalar()

    # TOTAL PROFIT
    selled_products = SelledProducts.query.join(DailySells).filter(DailySells.payment_status != 'pending').all()
    total_profit = 0
    for product in selled_products:
        total_profit += product.calculate_profit()

    today = datetime.utcnow().strftime('%d %b, %Y')

    for sell in allsell:
        if sell.payment_status != 'pending':
            sellprice += int(sell.totalprice) 
        
        if sell.payment_status == 'pending':
            pendingprice += int(sell.totalprice)

    obj = {
        "message": "GET Sell Successfully",
        "todaydate": today,
        "stock": stock,
        "selledtk": sellprice,
        "pendingtk": pendingprice,
        "totalselledproduct": totalselleproduct,
        "totalprofit": total_profit
    }
    res =  make_response(jsonify(obj), 200)
    return res



#   GET THIS MONTH SELL INFO
@dashboard.route('/api/sell/currentmonth/info/get/', methods=['POST'])
@login_required
def current_month_sell_info_get():
    current_month = datetime.utcnow().strftime("%m")

    # TOTAL SELED PRODUCT
    total_selled_products = SelledProducts.query.with_entities(func.sum(SelledProducts.quantity)).join(DailySells).filter(extract('month', DailySells.pub_date) == current_month).scalar()

    # TOTAL PROFIT
    selled_products = SelledProducts.query.join(DailySells).filter(and_(extract('month', DailySells.pub_date) == current_month, DailySells.payment_status != 'pending')).all()
    total_profit = 0
    for product in selled_products:
        total_profit += product.calculate_profit()

    today = datetime.utcnow().strftime('%d %b, %Y')

    # Get the total sell price and pending price for the current month
    sell_price, pending_price = 0, 0
    for sell in DailySells.query.all():
        sell_month = sell.pub_date.strftime("%m")
        if sell_month == current_month:
            if sell.payment_status != 'pending':
                sell_price += int(sell.totalprice)
            elif sell.payment_status == 'pending':
                pending_price += int(sell.totalprice)

    obj = {
        "message": "GET Sell Successfully",
        "selledtk": sell_price,
        "pendingtk": pending_price,
        "todaydate": today,
        "totalsellproduct": total_selled_products,
        "profit": total_profit
    }
    return make_response(jsonify(obj), 200)


# UPDATE PAYMENT STATUS
@dashboard.route('/api/sell/update/payment/status/<invoice_id>', methods=['POST'])
@login_required
def update_payment_status(invoice_id):
    # Get the new payment status from the POST request
    new_payment_status = request.json['payment_status']

    # Update the payment status in the database for the specific invoice
    sell = DailySells.query.filter_by(invoiceid=invoice_id).first()
    sell.payment_status = new_payment_status
    db.session.commit()

    flash('Payment Status Updated ✅', 'success')
    # Return a success message to the frontend
    return jsonify({'message': 'Payment status updated successfully'})


#   CUSTOMERWISE REPORT
@dashboard.route('/api/customer/<int:customer_id>/history')
@login_required
def get_customer_history(customer_id):
    # Query the customer by id
    customer = Customers.query.get(customer_id)
    if not customer:
        # Return a 404 error if the customer does not exist
        return make_response(jsonify({'error': 'Customer not found'}), 404)

    # Query the customer's orders from the DailySells table
    orders = DailySells.query.filter_by(customer_id=customer_id).all()
    if not orders:
        # Return a 404 error if the customer has no orders
        return make_response(jsonify({'error': 'No orders found for this customer'}), 404)

    # Create a list to store the customer's order history
    order_history = []
    for order in orders:
        # Query the products for each order
        products = SelledProducts.query.filter_by(daily_sells_id=order.id).all()
        # Create a dictionary to store the order's details
        order_details = {
            'invoice_id': order.invoiceid,
            'date': order.pub_date,
            'products': [{'name': product.productname, 'price': product.price, 'quantity': product.quantity} for product in products],
            'total_price': order.totalprice
        }
        # Append the order details to the customer's order history
        order_history.append(order_details)

    # Query the customer's total payment and pending payment
    total_payment = db.session.query(db.func.sum(DailySells.totalprice)).filter(DailySells.customer_id == customer_id).scalar()
    pending_payment = db.session.query(db.func.sum(DailySells.totalprice)).filter(DailySells.customer_id == customer_id, DailySells.payment_status == 'pending').scalar()
    if total_payment is None:
        total_payment = 0
    if pending_payment is None:
        pending_payment = 0

    # Return the customer's order history and payment details
    return jsonify({'order_history': order_history, 'total_payment': total_payment, 'pending_payment': pending_payment})


#   GET FILTERED REPORT
@dashboard.route('/dashboard/report/submit/', methods=['POST'])
@login_required
def get_report():
    data = request.get_json()

    start_date = data['startDate'] 
    end_date = data['endDate']
    filter = data['filter']

    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    if filter == 'all':
        invoices = DailySells.query.filter(DailySells.pub_date.between(start_date, end_date)).all()
    elif filter == 'pending':
        invoices = DailySells.query.filter(DailySells.pub_date.between(start_date, end_date), DailySells.payment_status == 'pending').all()
    elif filter == 'non-pending':
        invoices = DailySells.query.filter(DailySells.pub_date.between(start_date, end_date), DailySells.payment_status != 'pending').all()
    elif filter == 'products':
        # Query all products sold in the given date range
        invoices = DailySells.query.filter(DailySells.pub_date.between(start_date, end_date)).all()
        invoices_json = [invoice.to_dict() for invoice in invoices]
        products = []
        total_quantity = 0
        for invoice in invoices_json:
            for selled_product in invoice['selled_products']:
                productid = selled_product['productid']
                productname = selled_product['productname']
                quantity = selled_product['quantity']
                total_quantity += int(quantity)
                products.append({'productid': productid, 'productname': productname, 'quantity': quantity})
        
        return jsonify(products=products, total_quantity=total_quantity)
    else:
        # Return an error message if the filter option is not valid``
        return jsonify(error="Invalid filter option")
    
    # added code to convert DailySells objects to json serializable dict
    invoices_json = [invoice.to_dict() for invoice in invoices]

    # CALCULATING PROFIT
    total_profit = 0
    for invoice in invoices_json:
        if invoice['payment_status'] != 'pending':
            for selled_product in invoice['selled_products']:
                selled_product_obj = SelledProducts.query.filter_by(productname=selled_product['productname']).first()
                if selled_product_obj:
                    total_profit += selled_product_obj.calculate_profit()

    # CALCULATING PENDING
    total_pending = 0
    for invoice in invoices_json:
        if invoice['payment_status'] == 'pending':
            total_pending_products = 0
            for product in invoice['selled_products']:
                product_info = SelledProducts.query.filter_by(productname=product['productname'], daily_sells_id=invoice['id']).first()
                if product_info:
                    total_pending_products += product_info.calculate_profit()
            total_pending += total_pending_products

    return jsonify(invoices=invoices_json, total_pending=total_pending, total_profit=total_profit)
#   =======================
#   END API
#   =======================


#   ========================
#   START - REALTIME SEARCH
#   ========================

#   PRODUCT SEARCH by PRODUCT NAME
@dashboard.route('/dashboard/search-products-by-name')
@login_required
def search_products_id():
    search_query = request.args.get('q')
    products = Products.query.filter(Products.name.like(f'%{search_query}%')).all()
    return jsonify([product.to_dict() for product in products])


#   PRODUCT SEARCH by PRODUCT ID
@dashboard.route('/dashboard/search-products-by-id')
@login_required
def search_products_name():
    search_query = request.args.get('q')
    products = Products.query.filter(Products.productid.like(f'%{search_query}%')).all()
    return jsonify([product.to_dict() for product in products])


#   ORDER SEARCH
@dashboard.route('/dashboard/search-invoice')
@login_required
def search_orders():
    search_query = request.args.get('q')
    invoices = DailySells.query.filter(DailySells.invoiceid.like(f'%{search_query}%')).all()
    return jsonify([invoice.to_dict() for invoice in invoices])

#   ========================
#   END - REALTIME SEARCH
#   ========================


#   =============================
#   START DASHBAORD FUNCTIONALITY
#   =============================
@dashboard.route('/register/createadmin/', methods=['GET', 'POST'])
def registeradmin():
    current_ip = request.remote_addr
    if current_user.is_authenticated:
        current_user.ip = current_ip
        db.session.commit()
        return redirect(url_for('dashboard.admin_dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Users(phone=form.phone.data, username=form.username.data, email=form.email.data, password=hashed_password, user_role='admin')
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in ✅', 'success')
        return redirect(url_for('dashboard.admin_login'))

    return render_template('public/register.html', form=form, title='Register admin')


@dashboard.route('/register/', methods=['GET', 'POST'])
def register():
    current_ip = request.remote_addr
    if current_user.is_authenticated:
        current_user.ip = current_ip
        db.session.commit()
        return redirect(url_for('dashboard.admin_dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Users(phone=form.phone.data, username=form.username.data, email=form.email.data, password=hashed_password, user_role='user')
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in ✅', 'success')
        return redirect(url_for('dashboard.admin_login'))

    return render_template('public/register.html', form=form)


#   ADMIN LOGIN
@dashboard.route('/login/', methods=['GET', 'POST'])
def admin_login():
    current_ip = request.remote_addr
    if current_user.is_authenticated:
        current_user.ip = current_ip
        db.session.commit()
        return redirect(url_for('dashboard.admin_dashboard'))
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


#   USER PROFILE
@dashboard.route('/dashboard/profile/')
@login_required
def user_profile():
    user = current_user
    profile_picture = url_for('static', filename='profile_picture/' + current_user.profile)
    return render_template('dashboard/profile.html', user=user, title='Profile', profile_picture=profile_picture, shopname=shopname)


#   EDIT USER PROFILE
@dashboard.route('/dashboard/profile/update/', methods=['GET', 'POST'])
@login_required
def user_profile_edit():
    form = UpdateProfileForm()
    updated_fields = []

    # Check if form is submitted and valid
    if form.validate_on_submit():

        # Get form data
        new_password = form.new_password.data
        confirm_new_password = form.confirm_password.data
        current_password = form.current_password.data

        # Check if current password is correct
        current_password_hash = bcrypt.check_password_hash(current_user.password, current_password)
        if current_password_hash and new_password == confirm_new_password:
            # Hash and set new password
            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            current_user.password = hashed_password
            updated_fields.append("password")
            db.session.commit()

        elif current_password_hash and new_password != confirm_new_password:
            flash('New Password and Confirm Password Doesn\'t Matched ⚠️', 'danger')
            return redirect(url_for('dashboard.user_profile_edit'))

        elif current_password and current_password_hash == False:
            flash('Your current password is incorrect', 'danger')
            return redirect(url_for('dashboard.user_profile_edit'))
            
        if current_user.username != form.username.data:
            current_user.username = form.username.data
            updated_fields.append("username")

        if current_user.email != form.email.data:
            current_user.email = form.email.data
            updated_fields.append("email")
        
        if current_user.phone != form.phone.data:
            current_user.phone = form.phone.data
            updated_fields.append("phone")
        
        db.session.commit()
        
        if len(updated_fields) > 0:
            flash(f'Your {", ".join(updated_fields)} has been updated', 'success')
        return redirect(url_for('dashboard.user_profile'))

        # Check if profile picture is being updated
        # if form.picture.data:
        #     # Save new profile picture
        #     picture_file = save_profile_picture(form.picture.data)
        #     current_user.profile = picture_file
    
    if request.method == 'GET':
        form.phone.data = current_user.phone
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template('dashboard/profile_edit.html', title='Update Profile', form=form, shopname=shopname)

#   ADMIN DASHBOARD
@dashboard.route('/dashboard/')
@login_required
def admin_dashboard():
    # UPDATING INVOICE NUMBER FROM DB
    # daily_sells = DailySells.query.all()
    # for daily_sell in daily_sells:
    #     # Create new invoice id using uuid and current date and time
    #     new_invoice_id = datetime.now().strftime('%Y%m%d%H%M%S')+str(uuid.uuid4().int)[:6]
    #     # Update the invoice id in the database
    #     daily_sell.invoiceid = new_invoice_id
    #     db.session.commit()

    page = request.args.get('page', 1, type=int)
    sells = DailySells.query.order_by(DailySells.pub_date.desc()).paginate(page=page, per_page=50)
    # totalselledproduct = SelledProducts.query.all()
    return render_template('dashboard/dashboard.html', title='Dashboard', sells=sells, shopname=shopname)


#   DAILY SELL
@dashboard.route('/dashboard/todaysell/', methods=['GET', 'POST'])
@login_required
def todaysell():
    today = datetime.utcnow().strftime('%d %b, %Y')
    page = request.args.get('page', 1, type=int)
    sells = DailySells.query.order_by(DailySells.pub_date.desc()).paginate(page=page, per_page=50)

    return render_template('dashboard/todaysell.html', title='Today\'s Sell', sells=sells, today=today, shopname=shopname)


#   NEW SELL
@dashboard.route('/dashboard/newsell/', methods=['GET', 'POST'])
@login_required
def newsell():
    form=AddTodaySellForm()
    newinvoiceID = invoiceID()
    form.customer_name.choices = [(customer.id, customer.customer_name) for customer in Customers.query.all()]
    form.product_name.choices = [(product.productid, product.name) for product in Products.query.all()]

    return render_template('dashboard/newsell.html', title="New Sell", form=form, newinvoiceID=newinvoiceID, current_time=datetime.utcnow())


#   NEW SELL POS
@dashboard.route('/dashboard/newsell/pos/', methods=['GET', 'POST'])
@login_required
def newsellPOS():
    form=AddTodaySellForm()
    newinvoiceID = invoiceID()
    form.customer_name.choices = [(customer.id, customer.customer_name) for customer in Customers.query.all()]
    # form.product_name.choices = [(product.productid, product.name) for product in Products.query.all()]

    return render_template('dashboard/newsellPOS.html', title="New Sell", form=form, newinvoiceID=newinvoiceID, shopname=shopname)

@dashboard.route('/dashboard/newsell/submit/', methods=['POST'])
@login_required
def newsell_submit():
    userid = current_user.id

    strreq = request.get_json()
    data = json.loads(strreq)
   
    print("==================")
    print(data)
    print("==================")
    
    subtotal = data['cashier']['subtotal']
    discount = data['cashier']['discount']
    totalprice = data['cashier']['total']
    print('Showing pricing ---->>')
    print(f'Subtotal: {subtotal}')
    print(f'Discount: {discount}')
    print(f'Total Price: {totalprice}')

    invoice_id = data['invoiceid']
    customerid = data['customer']['customer_id']
    paymentstatus = data['customer']['payment_status']
    transactionid = data['customer']['transactionid']
    note = data['customer']['note']
    pub_date = datetime.strptime(data['pub_date'].strip('"'), "%Y-%m-%dT%H:%M")


    print('-------->>>')
    print(f'Invoice ID: {invoice_id}')
    print(f'Customer ID: {customerid}')
    print(f'Payment Status: {paymentstatus}')
    print(f'Transaction ID: {transactionid}')
    print(f'Note: {note}')
    print(f'Pub Date: {pub_date}')
    print(";;;;;;;;;;;;;;;;;;;;;;  DONE  ;;;;;;;;;;;;;;;;;;;;;")

    dailysell = DailySells(customer_id=customerid, invoiceid=invoice_id, subtotal=subtotal, discount=discount, totalprice=totalprice,payment_status=paymentstatus, trnx_id=transactionid, note=note, user_id=userid, pub_date=pub_date)
    
    db.session.add(dailysell)
    db.session.commit()

    print(f'daily sell id ---->> {dailysell.id}')
    print('Showing all products ---->>')

    products = data['products']
    for product in products:
        print(f"Product Name: {product['productname']}")
        print(f"Product id: {product['productid']}")
        print(f"Product price: {product['price']}")
        # print(f"Product buying price: {product['buying_price']}")
        print(f"Product quantity: {product['quantity']}")
        print(f"Product unit total: {product['unittotal']}")
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        current_product = product['productid']
        current_product_quantity = product['quantity']
        # fetch all products for update the product quantity
        get_product = Products.query.filter_by(productid=current_product).first()
        update_product_stock = int(get_product.stock) - int(current_product_quantity)
        get_product.stock = update_product_stock
        selled_product = SelledProducts(productname=product['productname'], productid=product['productid'], price=product['price'], quantity=product['quantity'],unittotal=product['unittotal'], daily_sells_id=dailysell.id)
        
        db.session.add(selled_product)
    db.session.commit()

    res =  make_response(jsonify({"message": "Sell Completed Successfully"}), 200)

    return res

#   VIEW INVOICE
@dashboard.route('/dashboard/sell/<string:invoiceid>/')
@login_required
def view_sell(invoiceid):
    sell = DailySells.query.filter_by(invoiceid=invoiceid).first()
    products = SelledProducts.query.filter_by(daily_sells_id=sell.id).all()
    customer = Customers.query.filter_by(id=sell.customer_id).first()
    user = Users.query.filter_by(id=sell.user_id).first()
    
    return render_template('/dashboard/sell.html', products=products, sell=sell, customer=customer, user=user, shopname=shopname)


#   PRINT INVOICE
@dashboard.route('/dashboard/sell/<string:invoiceid>/print/')
@login_required
def print_pos_sell(invoiceid):
    sell = DailySells.query.filter_by(invoiceid=invoiceid).first()
    products = SelledProducts.query.filter_by(daily_sells_id=sell.id).all()
    customer = Customers.query.filter_by(id=sell.customer_id).first()
    user = Users.query.filter_by(id=sell.user_id).first()
    
    return render_template('/dashboard/sell-pos-print.html', products=products, sell=sell, customer=customer, user=user)

# =====================================
#   LATEST VERSION PRINT INVOICE
# =====================================
# @app.route('/dashboard/sell/<string:invoiceid>/print')
# def print_invoice(invoiceid):
#     # Fetch the invoice data from the database
#     invoice = DailySells.query.filter_by(invoiceid=invoiceid).first()

#     # Create a new PDF document
#     response = make_response()
#     response.headers['Content-Type'] = 'application/pdf'
#     response.headers['Content-Disposition'] = 'attachment; filename=invoice.pdf'
#     pdf = canvas.Canvas(response.stream)

#     # Set the paper size to fit the thermal printer's paper width
#     pdf.setPageSize((80 * mm, A7[1]))

#     # Add the invoice data to the PDF
#     pdf.drawString(10 * mm, A7[1] - 10 * mm, f'Invoice Number: {invoice.invoice_no}')
#     y = A7[1] - 20 * mm
#     for item in invoice.items:
#         pdf.drawString(10 * mm, y, item.product.name)
#         pdf.drawString(40 * mm, y, f'x{item.quantity}')
#         pdf.drawString(60 * mm, y, f'${item.subtotal}')
#         y -= 10 * mm
#     pdf.drawString(60 * mm, 10 * mm, f'Total: ${invoice.total}')

#     # Close the PDF document and return it as a response
#     pdf.showPage()
#     pdf.save()
#     return response



# def generate_invoice_pdf(invoice):
#     # Create a file-like buffer to receive PDF data.
#     buffer = BytesIO()

#     # Create the PDF object, using the buffer as its "file."
#     pdf = canvas.Canvas(buffer, pagesize=letter)

#     # Draw things on the PDF. Here's where the PDF generation happens.
#     # See the ReportLab documentation for the full list of functionality.
#     pdf.setTitle('Invoice #{0}'.format(invoice.id))
#     pdf.setFont('Helvetica', 12)
#     pdf.drawString(1 * inch, 10.5 * inch, 'Invoice #{0}'.format(invoice.id))
#     pdf.drawString(1 * inch, 10.25 * inch, 'Customer Name: {0}'.format(invoice.customer_name))
#     pdf.drawString(1 * inch, 10 * inch, 'Customer Address: {0}'.format(invoice.customer_address))

#     # Loop through the items in the invoice and add them to the PDF.
#     y = 9.5 * inch
#     for item in invoice.items:
#         pdf.drawString(1 * inch, y, item.product.name)
#         pdf.drawRightString(3.5 * inch, y, '${0:.2f}'.format(item.price))
#         y -= 0.25 * inch

#     # Add the total to the PDF.
#     pdf.setFont('Helvetica-Bold', 12)
#     pdf.drawString(1 * inch, y, 'Total:')
#     pdf.drawRightString(3.5 * inch, y, '${0:.2f}'.format(invoice.total))

#     # Close the PDF object cleanly, and we're done.
#     pdf.save()

#     # File response
#     pdf_file = buffer.getvalue()
#     buffer.close()
#     return pdf_file



#   BRAND
@dashboard.route('/dashboard/brand/', methods=['GET', 'POST'])
@login_required
def brand():
    #   FETCHING EXISTING BRAND
    brands = Brands.query.all()

    #   ADDING NEW BRAND
    form = AddBrandForm()
    if form.validate_on_submit():
        if form.brand_logo.data:
            picture_file = save_logo(form.brand_logo.data)
            brand = Brands(name=form.brand_name.data, logo=picture_file, note=form.brand_note.data)
        else:
            brand = Brands(name=form.brand_name.data, note=form.brand_note.data)
        db.session.add(brand)
        db.session.commit()
        flash(f'Brand "{form.brand_name.data}" added successfully ✅', 'success')
        return redirect(url_for('dashboard.brand'))
    return render_template('dashboard/brand.html', title='Brand', form=form, brands=brands, shopname=shopname)


#   EDIT BRAND
@dashboard.route("/dashboard/brand/<int:brand_id>/update/", methods=['GET', 'POST'])
@login_required
def edit_brand(brand_id):
    brand = Brands.query.get_or_404(brand_id)
    form = AddBrandForm()
    if form.validate_on_submit():
        if form.brand_logo.data:
            brand.name = form.brand_name.data
            if brand.logo and brand.logo != 'default.jpg':
                os.unlink(os.path.join(current_app.root_path,'static/brandlogo/' +  brand.logo))
            picture_file = save_logo(form.brand_logo.data)
            # brandlogo = url_for('static', filename='brandlogo/' + picture_file)
            brand.logo = picture_file
            brand.note = form.brand_note.data
            db.session.commit()
            flash('Brand details has been updated ✅', 'success')
        else:
            brand.name = form.brand_name.data
            brand.note = form.brand_note.data
            db.session.commit()
            flash('Brand details has been updated ✅', 'success')
        return redirect(url_for('dashboard.brand', brand_id=brand.id))
    
    if request.method == 'GET':
        form.brand_name.data = brand.name
        form.brand_logo.data = brand.logo
        form.brand_note.data = brand.note
    return render_template('dashboard/brand_edit.html', title='Edit Brand', form=form, brand=brand, shopname=shopname)


#   DELETE BRAND
@dashboard.route("/dashboard/brand/<int:brand_id>/delete/", methods=['POST'])
@login_required
def delete_brand(brand_id):
    brand = Brands.query.get_or_404(brand_id)
    if brand.logo and brand.logo != 'default.jpg':
        os.unlink(os.path.join(current_app.root_path,'static/brandlogo/' +  brand.logo))
    db.session.delete(brand)
    db.session.commit()
    flash(f'Brand "{brand.name}" has been deleted ✅', 'success')
    return redirect(url_for('dashboard.brand'))


#   CATEGORY
@dashboard.route('/dashboard/category/', methods=['GET', 'POST'])
@login_required
def category():
    #   FETCHING EXISTING CATEGORY
    categories = Categories.query.all()

    #   ADDING NEW CATEGORY
    form = AddCategoryForm()
    if form.validate_on_submit():
        category = Categories(name=form.category_name.data, note=form.category_note.data)
        db.session.add(category)
        db.session.commit()
        flash(f'Category "{form.category_name.data}" added successfully ✅', 'success')
        return redirect(url_for('dashboard.category'))
    return render_template('dashboard/category.html', title='Category', form=form, categories=categories, shopname=shopname)


#   EDIT CATEGORY
@dashboard.route("/dashboard/category/<int:category_id>/update/", methods=['GET', 'POST'])
@login_required
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
    return render_template('dashboard/category_edit.html', form=form, category=category, shopname=shopname)


#   DELETE CATEGORY
@dashboard.route("/dashboard/category/<int:category_id>/delete/", methods=['POST'])
@login_required
def delete_category(category_id):
    category = Categories.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash(f'Category "{category.name}" Deleted ✅', 'success')
    return redirect(url_for('dashboard.category'))


#   PRODUCTS
@dashboard.route('/dashboard/products/', methods=['GET', 'POST'])
@login_required
def products():
    form=AddProductForm()
    form.product_brand.choices = [(brand.id, brand.name) for brand in Brands.query.all()]
    form.product_category.choices = [(category.id, category.name) for category in Categories.query.all()]
    
    page = request.args.get('page', 1, type=int)
    products = Products.query.order_by(Products.pub_date.desc()).paginate(page=page, per_page=50)
    brands = Brands.query.all()
    categories = Categories.query.all()

    # count total stock
    total_products = Products.query.with_entities(func.sum(Products.stock)).scalar()

    if form.validate_on_submit():
        productname = form.product_name.data.strip()
        productID = form.product_id.data.strip()
        productprice = int(str(form.product_price.data).strip())
        productBuyingprice = int(str(form.product_buying_price.data).strip())
        productquantity = int(str(form.product_quantity.data).strip())
        productdescription = form.product_description.data.strip()
        productbrand = form.product_brand.data.strip()
        productcategory = form.product_category.data.strip()
        productimage = form.product_image.data
        productStatus = form.product_available.data

        if productimage:
            picture_file = save_product(productimage)
            # imagefile = url_for('static', filename='productimages/' + picture_file)
            product = Products(name=productname, productid=productID, price=productprice, 
                                buying_price=productBuyingprice, 
                                stock=productquantity, description= productdescription, brand_id=productbrand, 
                                category_id= productcategory, image1=picture_file, available_status=productStatus)  
            # STORING IN DB
            db.session.add(product)
            db.session.commit()
            return redirect(url_for('dashboard.products'))    
        
        product = Products(name=productname, productid=productID, price=productprice,
                            buying_price=productBuyingprice,  
                            stock=productquantity, description=productdescription, brand_id=productbrand, 
                            category_id=productcategory, available_status=productStatus)  
        
        #   STORING IN DB
        db.session.add(product)
        db.session.commit()

        return redirect(url_for('dashboard.products'))

    return render_template('dashboard/products.html', title='Products', form=form, brands=brands, categories=categories, products=products, total_products=total_products, shopname=shopname)

#   GENERATE BARCODE FOR PRODUCTS
@dashboard.route('/barcode/<int:product_id>/')
def generate_barcode(product_id):
    # Generate a Code 128 barcode for the given product ID
    code = barcode.get('code128', str(product_id), writer=ImageWriter())
    output = BytesIO()
    code.write(output)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response

@dashboard.route('/barcode/<int:product_id>/print')
def print_barcode(product_id):
    # Generate a Code 128 barcode for the given product ID
    return render_template('dashboard/barcode-print.html')

#   EDIT PRODUCTS
@dashboard.route("/dashboard/product/<int:product_id>/update/", methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Products.query.get_or_404(product_id)
    
    form = EditProductForm()
    form.product_brand.choices = [(product.brand_id, Brands.query.get(product.brand_id).name)] + [(brand.id, brand.name) for brand in Brands.query.filter(Brands.id != product.brand_id).all()]

    form.product_category.choices = [(product.category_id, Categories.query.get(product.category_id).name)] + [(category.id, category.name) for category in Categories.query.filter(Categories.id != product.category_id).all()]
    
    if form.validate_on_submit():
        productname = form.product_name.data.strip()
        productID = form.product_id.data.strip()
        productprice = int(str(form.product_price.data).strip())
        productBuyingprice = int(str(form.product_buying_price.data).strip())
        productquantity = int(str(form.product_quantity.data).strip())
        productdescription = form.product_description.data.strip()
        productStatus = form.product_available.data
        if form.product_brand.data:
            productbrand = form.product_brand.data

        if form.product_category.data:
            productcategory = form.product_category.data
        
        productimage = form.product_image.data

        #   CHECK IF NEW IMAGE ADDED
        if productimage:
            if product.image1 != 'demoproduct.jpg':
                os.unlink(os.path.join(current_app.root_path,'static/productimages/' +  product.image1))
            picture_file = save_product(productimage)
            product.image1 = picture_file
        
        product.name = productname
        product.productid = productID
        product.price = productprice
        product.buying_price = productBuyingprice
        product.stock = productquantity
        product.description = productdescription
        product.brand_id = productbrand
        product.category_id = productcategory
        product.available_status = productStatus
        product.pub_date = datetime.utcnow()
        db.session.commit()
        flash('Product details has been updated ✅', 'success')
        return redirect(url_for('dashboard.products'))

    if request.method == 'GET':
        form.product_name.data = product.name
        form.product_id.data = product.productid
        form.product_price.data = product.price 
        form.product_buying_price.data = product.buying_price
        form.product_quantity.data = product.stock 
        form.product_description.data = product.description 
        form.product_available.data = product.available_status
    return render_template('dashboard/product_edit.html', form=form, product=product, shopname=shopname)


#   SHOW A PRODUCT INFO
@dashboard.route("/dashboard/product/<int:product_id>/")
@login_required
def show_product(product_id):
    product = Products.query.get_or_404(product_id)
    return render_template('dashboard/product_details.html', product=product, shopname=shopname)


#   DELTE A PRODUCT
@dashboard.route("/dashboard/product/<int:product_id>/delete/", methods=['POST'])
@login_required
def delete_product(product_id):
    product = Products.query.get_or_404(product_id)
    if product.image1 != 'demoproduct.jpg':
        os.unlink(os.path.join(current_app.root_path,'static/productimages/' +  product.image1))
    db.session.delete(product)
    db.session.commit()
    flash('Your product has been deleted ✅', 'success')
    return redirect(url_for('dashboard.products'))


#   ORDERS
@dashboard.route('/dashboard/orders/', methods=['GET', 'POST'])
@login_required
def orders():
    return render_template('dashboard/orders.html', title='Orders', shopname=shopname)

#   CUSTOMER
@dashboard.route('/dashboard/customers/', methods=['GET', 'POST'])
@login_required
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
    return render_template('dashboard/customer.html', title='Customer', form=form, customers=customers, total_customer=total_customer, shopname=shopname)


#   CUSTOMERWISE REPORT
@dashboard.route('/customer/<int:customer_id>/payment-history/')
@login_required
def customer_payment_history(customer_id):
    page = request.args.get('page', 1, type=int)
    customer = Customers.query.filter_by(id=customer_id).first()
    orders = DailySells.query.filter_by(customer_id=customer_id).order_by(DailySells.pub_date.desc()).paginate(page=page, per_page=50)
    total_payment = 0
    pending_payment = 0
    for order in orders.items:
        total_payment += int(order.totalprice)
        if order.payment_status == 'pending':
            pending_payment += int(order.totalprice)
    return render_template('dashboard/customer_history.html', customer=customer, orders=orders, total_payment=total_payment, pending_payment=pending_payment, shopname=shopname)


#   EDIT CUSTOMER
@dashboard.route("/dashboard/customer/<int:customer_id>/update/", methods=['GET', 'POST'])
@login_required
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
    return render_template('dashboard/customer_edit.html', form=form, shopname=shopname)


#   DELETE CUSTOMER
@dashboard.route("/dashboard/customer/<int:customer_id>/delete/", methods=['POST'])
@login_required
def delete_customer(customer_id):
    customer = Customers.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    flash(f'Customer "{customer.customer_name}" Deleted ✅', 'success')
    return redirect(url_for('dashboard.customer'))

#   REPORT
@dashboard.route('/dashboard/report/', methods=['GET'])
@login_required
def report():
    return render_template('dashboard/report.html', title='Report', shopname=shopname)
#   =============================
#   END DASHBAORD FUNCTIONALITY
#   =============================