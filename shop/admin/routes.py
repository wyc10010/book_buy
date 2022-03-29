from flask import render_template,session, redirect,url_for,flash
from flask_login import logout_user
from shop import app,db,bcrypt
from .forms import RegistrationForm,LoginForm
from .models import User
from shop.products.models import Addproduct,Category, Author
from shop.customers.model import Coupon, CustomerOrder, Register

# @app.route('/users')
# def users():
#     users = User.query.all()
#     return render_template('admin/user.html', title='Admin page', users=users)

@app.route('/products')
def products():
    products = Addproduct.query.all()
    return render_template('admin/product.html', title='products', products=products)

@app.route('/categories')
def categories():
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template('admin/category.html', title='categories', categories=categories)

@app.route('/authors')
def authors():
    authors = Author.query.all()
    return render_template('admin/author.html', title='authors', authors=authors)

@app.route('/coupons')
def coupons():
    coupons = Coupon.query.order_by(Coupon.type.desc()).all()
    return render_template('admin/coupon.html', title='coupons', coupons=coupons)
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        user = User(name=form.name.data,username=form.username.data, email=form.email.data,
                    password=hash_password)
        db.session.add(user)
        flash(f'Welcome {form.name.data}, Thanks for registering!','success')
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('admin/register.html',title='Register user', form=form)


@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['email'] = form.email.data
            flash(f'Welcome {user.username}, you are logedin now.','success')
            return redirect(url_for('dashboard'))
        else:
            flash(f'Wrong Admin Email and Password.', 'danger')
            return redirect(url_for('login'))
    return render_template('admin/login.html',title='Login page',form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash(f'You are Logout!', 'success')
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    if 'email' not in session:
        flash('Login your account, thanks.', 'danger')
        return redirect(url_for('login'))
    user = User.query.all()
    products = Addproduct.query.all()
    orders = CustomerOrder.query.all()
    qry2021Dec = CustomerOrder.query.filter(CustomerOrder.date_created.between('2021-12-01', '2021-12-31'))
    qry2022Jan = CustomerOrder.query.filter(CustomerOrder.date_created.between('2022-01-01', '2022-01-31'))
    customer_orders =  CustomerOrder.query.all()
    allPriceList = []
    allDiscountList = []
    allQuantity = []

    DecPriceList = []
    DecDiscountList = []
    DecQuantity = []

    JanPriceList = []
    JanDiscountList = []
    JanQuantity = []

    order_list = ["6","4","3","2","22","12"]
    for order_detail in customer_orders:
        for i in order_list:
            order = order_detail.orders.get(i)
            if type(order) is dict:
                for key, value in order.items():
                    if key == 'price':
                        allPriceList.append(value)
                    elif key == 'quantity':
                        allQuantity.append(int(value))
                    if key == 'discount':
                        if  value != 0:
                            discount_percent = (value/100)
                            allDiscountList.append(discount_percent)
                        else:
                            allDiscountList.append(1)
    all = [(round(x*y*z)) for x,y,z in zip(allPriceList,allDiscountList,allQuantity)]
    allPrice = sum(i for i in all)

    for order_detail in qry2021Dec:
        for i in order_list:
            order = order_detail.orders.get(i)
            if type(order) is dict:
                for key, value in order.items():
                    if key == 'price':
                        DecPriceList.append(value)
                    elif key == 'quantity':
                        DecQuantity.append(int(value))
                    if key == 'discount':
                        if  value != 0:
                            discount_percent = (value/100)
                            DecDiscountList.append(discount_percent)
                        else:
                            DecDiscountList.append(1)
    Dec = [(round(x*y*z)) for x,y,z in zip(DecPriceList,DecQuantity,DecDiscountList)]
    DecPrice = sum(i for i in Dec)

    for order_detail in qry2022Jan:
        for i in order_list:
            order = order_detail.orders.get(i)
            if type(order) is dict:
                for key, value in order.items():
                    if key == 'price':
                        JanPriceList.append(value)
                    elif key == 'quantity':
                        JanQuantity.append(int(value))
                    if key == 'discount':
                        if  value != 0:
                            discount_percent = (value/100)
                            JanDiscountList.append(discount_percent)
                        else:
                            JanDiscountList.append(1)
    Jan = [(round(x*y*z)) for x,y,z in zip(JanPriceList,JanQuantity,JanDiscountList)]
    JanPrice = sum(i for i in Jan)


    return render_template('admin/dashboard.html',customer_orders=customer_orders,allPrice=allPrice,
    DecPrice=DecPrice,JanPrice=JanPrice,title='Admin dashboard', user=user, orders=orders, products=products)


@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        flash('Login your account, thanks.', 'danger')
        return redirect(url_for('login'))
    user = User.query.all()
    products = Addproduct.query.all()
    orders = CustomerOrder.query.all()

    qry2021Dec = CustomerOrder.query.filter(CustomerOrder.date_created.between('2021-12-01', '2021-12-31'))
    qry2022Jan = CustomerOrder.query.filter(CustomerOrder.date_created.between('2022-01-01', '2022-01-31'))
    customer_orders =  CustomerOrder.query.all()
    allPriceList = []
    allDiscountList = []
    allQuantity = []

    DecPriceList = []
    DecDiscountList = []
    DecQuantity = []

    JanPriceList = []
    JanDiscountList = []
    JanQuantity = []

    order_list = ["6","4","3","2","22","12"]
    for order_detail in customer_orders:
        for i in order_list:
            order = order_detail.orders.get(i)
            if type(order) is dict:
                for key, value in order.items():
                    if key == 'price':
                        allPriceList.append(value)
                    elif key == 'quantity':
                        allQuantity.append(int(value))
                    if key == 'discount':
                        if  value != 0:
                            discount_percent = (value/100)
                            allDiscountList.append(discount_percent)
                        else:
                            allDiscountList.append(1)
    all = [(round(x*y*z)) for x,y,z in zip(allPriceList,allDiscountList,allQuantity)]
    allPrice = sum(i for i in all)

    for order_detail in qry2021Dec:
        for i in order_list:
            order = order_detail.orders.get(i)
            if type(order) is dict:
                for key, value in order.items():
                    if key == 'price':
                        DecPriceList.append(value)
                    elif key == 'quantity':
                        DecQuantity.append(int(value))
                    if key == 'discount':
                        if  value != 0:
                            discount_percent = (value/100)
                            DecDiscountList.append(discount_percent)
                        else:
                            DecDiscountList.append(1)
    Dec = [(round(x*y*z)) for x,y,z in zip(DecPriceList,DecQuantity,DecDiscountList)]
    DecPrice = sum(i for i in Dec)

    for order_detail in qry2022Jan:
        for i in order_list:
            order = order_detail.orders.get(i)
            if type(order) is dict:
                for key, value in order.items():
                    if key == 'price':
                        JanPriceList.append(value)
                    elif key == 'quantity':
                        JanQuantity.append(int(value))
                    if key == 'discount':
                        if  value != 0:
                            discount_percent = (value/100)
                            JanDiscountList.append(discount_percent)
                        else:
                            JanDiscountList.append(1)
    Jan = [(round(x*y*z)) for x,y,z in zip(JanPriceList,JanQuantity,JanDiscountList)]
    JanPrice = sum(i for i in Jan)


    return render_template('admin/dashboard.html',customer_orders=customer_orders,allPrice=allPrice,
    DecPrice=DecPrice,JanPrice=JanPrice,title='Admin dashboard', user=user, orders=orders, products=products)