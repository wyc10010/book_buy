from flask import render_template,session, request,redirect,url_for,flash,current_app,make_response
from flask import request
from flask_login import login_required, current_user, logout_user, login_user
from shop import app,db,photos, search,bcrypt,login_manager
from .forms import CustomerRegisterForm, CustomerLoginFrom, CouponForm,OrderCouponForm
from .model import Register, CustomerOrder, Coupon
import secrets
import os
import json
import pdfkit
import stripe
import math

publishable_key ='pk_test_51KBIsdB2A3ZYpECUxZOZt7x5V2jXKJCPdZU5p1gCV6H3S6VD7u7FPch8l3ydddPM8jbRk1fFgA1tCU8NaoJ61z2G00BZF2NRL6'
stripe.api_key ='sk_test_51KBIsdB2A3ZYpECUev6H8YAdbVMOnWy5NVuaT5EOBbVFbZYsJiZkQ0DXEIfHLtv7id8sMUzs2V3BjqKEUt41xfrV00DQb9HUVi'

@app.route('/payment', methods=['GET','POST'])
def payment():
    invoice = request.form.get('invoice')
    amount = request.form.get('amount')
    customer = stripe.Customer.create(
      email=request.form['stripeEmail'],
      source=request.form['stripeToken'],
    )
    charge = stripe.Charge.create(
      customer=customer.id,
      description='Myshop',
      amount=amount,
      currency='TWD',
    )
    orders =  CustomerOrder.query.filter_by(customer_id = current_user.id,invoice=invoice).order_by(CustomerOrder.id.desc()).first()
    orders.status = 'Paid'
    db.session.commit()
    return redirect(url_for('thanks'))

@app.route('/thanks')
def thanks():
    return render_template('customer/thank.html')


@app.route('/customer/register', methods=['GET','POST'])
def customer_register():
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        register = Register(name=form.name.data, username=form.username.data, email=form.email.data, password=hash_password, contact=form.contact.data, address=form.address.data, zipcode=form.zipcode.data)
        db.session.add(register)
        flash(f'Welcome {form.name.data}. Thank you for registering', 'success')
        db.session.commit()
        return redirect(url_for('customer_login'))
    return render_template('customer/register.html', form=form)


@app.route('/customer/login', methods=['GET','POST'])
def customer_login():
    form = CustomerLoginFrom()
    if form.validate_on_submit():
        user = Register.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You are login now!', 'success')
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        flash('Incorrect email and password','danger')
        return redirect(url_for('customer_login'))
            
    return render_template('customer/login.html', form=form)


@app.route('/customer/logout')
def customer_logout():
    logout_user()
    return redirect(url_for('home'))

def updateshoppingcart():
    for key, shopping in session['Shoppingcart'].items():
        session.modified = True
        del shopping['image']
        del shopping['author']
    return updateshoppingcart

@app.route('/getorder')
@login_required
def get_order():
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        updateshoppingcart
        try:
            order = CustomerOrder(invoice=invoice,customer_id=customer_id,orders=session['Shoppingcart'])
            db.session.add(order)
            db.session.commit()
            session.pop('Shoppingcart')
            flash('Your order has been sent successfully','success')
            return redirect(url_for('orders',invoice=invoice))
        except Exception as e:
            print(e)
            flash('Some thing went wrong while get order', 'danger')
            return redirect(url_for('getCart'))
        
@app.route('/orders/<invoice>')
@login_required
def orders(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        customer = Register.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
        coupons = Coupon.query.order_by(Coupon.type.desc()).all()
        coupon_discount_money = 100;
        new_grandTotal = 0;
        for _key, product in orders.orders.items():
            if product['discount'] > 0:
                discount = (product['discount']/100) * int(product['price'])
                subTotal += int(discount) * int(product['quantity'])
                delivery_fee = 60
                grandTotal = round(int(subTotal) + delivery_fee)
                if grandTotal > 2000:
                    new_grandTotal = grandTotal - coupon_discount_money
            else:
                subTotal += int(product['price']) * int(product['quantity'])
                delivery_fee = 60
                grandTotal = round(int(subTotal) + delivery_fee)
                if grandTotal > 2000:
                    new_grandTotal = grandTotal - coupon_discount_money
    else:
        return redirect(url_for('customerLogin'))
    return render_template('customer/order.html', invoice=invoice, delivery_fee=delivery_fee,subTotal=subTotal,grandTotal=grandTotal,customer=customer,orders=orders, coupons=coupons, coupon_discount_money=coupon_discount_money,new_grandTotal=new_grandTotal)



@app.route('/get_pdf/<invoice>', methods=['POST'])
@login_required
def get_pdf(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        if request.method =="POST":
            customer = Register.query.filter_by(id=customer_id).first()
            orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
            for _key, product in orders.orders.items():
                discount = (product['discount']/100) * float(product['price'])
                subTotal += float(product['price']) * int(product['quantity'])
                subTotal -= discount
                tax = ("%.2f" % (.06 * float(subTotal)))
                grandTotal = float("%.2f" % (1.06 * subTotal))

            rendered =  render_template('customer/pdf.html', invoice=invoice, tax=tax,grandTotal=grandTotal,customer=customer,orders=orders)
            pdf = pdfkit.from_string(rendered, False)
            response = make_response(pdf)
            response.headers['content-Type'] ='application/pdf'
            response.headers['content-Disposition'] ='inline; filename='+invoice+'.pdf'
            return response

@app.route('/add_coupon', methods=['GET', 'POST'])
def add_coupon():
    addCouponForm = CouponForm()
    if addCouponForm.validate_on_submit():
        coupon_name = addCouponForm.coupon_name.data
        type = addCouponForm.type.data
        coupon_discount = addCouponForm.coupon_discount.data
        coupon_limit_discount = addCouponForm.coupon_limit_discount.data
        quantity = addCouponForm.quantity.data
        start_date = addCouponForm.start_date.data
        end_date = addCouponForm.end_date.data
        
        coupon = Coupon(coupon_name=coupon_name, type=type, coupon_discount=coupon_discount, coupon_limit_discount=coupon_limit_discount,
                                quantity=quantity, start_date=start_date, end_date=end_date)
        db.session.add(coupon)
        flash(f'The coupon {addCouponForm.coupon_name.data} was added in database', 'success')
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('customer/addcoupon.html', form=addCouponForm, title='Add a Coupon')

@app.route('/delete_coupon/<int:id>', methods=['GET', 'POST'])
def delete_coupon(id):
    if 'email' not in session:
        flash('Login your account, thanks.', 'danger')
        return redirect(url_for('login'))
    coupons = Coupon.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(coupons)
        flash(
            f"The coupon '{coupons.coupon_name}' was deleted from your database.", "success")
        db.session.commit()
        return redirect(url_for('admin'))
    flash(
        f"The coupon '{coupons.coupon_name}' can't be deleted from your database.", "warning")
    return redirect(url_for('admin'))
