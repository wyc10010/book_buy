from flask import render_template, session, request, redirect, url_for, flash, current_app
from shop import app, db, photos, search
from .models import Category, Addproduct, Author
from .forms import Addproducts
import secrets
import os

def authors():
    authors = Author.query.all()
    return authors

def categories():
    categories = Category.query.join(
        Addproduct, (Category.id == Addproduct.category_id)).all()
    return categories

@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    products = Addproduct.query.filter(Addproduct.stock > 0).order_by(
        Addproduct.id.desc()).paginate(page=page, per_page=8)
    return render_template('products/index.html', products=products, categories=categories())

@app.route('/product_page')
def product_page():
    page = request.args.get('page', 1, type=int)
    products = Addproduct.query.filter(Addproduct.stock > 0).order_by(
        Addproduct.id.desc()).paginate(page=page, per_page=8)
    return render_template('products/products.html', products=products, categories=categories())

@app.route('/result')
def result():
    searchword = request.args.get('q')
    products = Addproduct.query.msearch(
        searchword, fields=['name', 'desc'], limit=6)
    authors = Author.query.msearch(
        searchword, fields=['name'], limit=6)
    return render_template('products/result.html', products=products, categories=categories(),authors=authors)


@app.route('/product/<int:id>')
def single_page(id):
    product = Addproduct.query.get_or_404(id)
    return render_template('products/single_page.html', product=product, categories=categories())


@app.route('/categories/<int:id>')
def get_category(id):
    page = request.args.get('page', 1, type=int)
    get_cat = Category.query.filter_by(id=id).first_or_404()
    get_cat_prod = Addproduct.query.filter_by(
        category=get_cat).paginate(page=page, per_page=8)
    return render_template('products/index.html', get_cat_prod=get_cat_prod, categories=categories(), get_cat=get_cat)


@app.route('/addcat', methods=['GET', 'POST'])
def addcat():
    if request.method == "POST":
        getcat = request.form.get('category')
        category = Category(name=getcat)
        db.session.add(category)
        flash(f'The category {getcat} was added to your database', 'success')
        db.session.commit()
        return redirect(url_for('addcat'))
    return render_template('products/addcategory.html', title='Add category')

@app.route('/updatecat/<int:id>', methods=['GET', 'POST'])
def updatecat(id):
    if 'email' not in session:
        flash('Login your account, thanks.', 'danger')
        return redirect(url_for('login'))
    updatecat = Category.query.get_or_404(id)
    category = request.form.get('category')
    if request.method == "POST":
        updatecat.name = category
        flash(
            f'The category was updated.', 'success')
        db.session.commit()
        return redirect(url_for('categories'))
    category = updatecat.name
    return render_template('products/addcategory.html', title='Update category', updatecat=updatecat)


@app.route('/deletecat/<int:id>', methods=['GET', 'POST'])
def deletecat(id):
    if 'email' not in session:
        flash('Login your account, thanks.', 'danger')
        return redirect(url_for('login'))
    category = Category.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(category)
        flash(
            f"The category '{category.name}' was deleted from your database.", "success")
        db.session.commit()
        return redirect(url_for('admin'))
    flash(
        f"The category '{category.name}' can't be deleted from your database.", "warning")
    return redirect(url_for('admin'))

@app.route('/addRelation', methods=['GET', 'POST'])
def addauthors_to_product():
    products = Addproduct.query.all()
    authors = Author.query.all()
    if request.method == "POST":
        product_id = request.form.get('product')
        author_id = request.form.get('author')
        product = Addproduct.query.filter_by(id=product_id).first()
        author = Author.query.filter_by(id=author_id).first()
        product.authors.append(author)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('products/book_author.html', title='Add a Product and Author', products=products,authors=authors)


@app.route('/addproduct', methods=['GET', 'POST'])
def addproduct():
    form = Addproducts(request.form)
    categories = Category.query.all()
    if request.method == "POST" and 'image_1' in request.files:
        name = form.name.data
        price = form.price.data
        discount = form.discount.data
        stock = form.stock.data
        desc = form.discription.data
        category = request.form.get('category')
        image_1 = photos.save(request.files.get(
            'image_1'), name=secrets.token_hex(10) + ".")
        image_2 = photos.save(request.files.get(
            'image_2'), name=secrets.token_hex(10) + ".")
        image_3 = photos.save(request.files.get(
            'image_3'), name=secrets.token_hex(10) + ".")
        addproduct = Addproduct(name=name, price=price, discount=discount, stock=stock,
                                desc=desc, category_id=category, image_1=image_1, image_2=image_2, image_3=image_3)
        db.session.add(addproduct)
        flash(f'The product {name} was added in database', 'success')
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('products/addproduct.html', form=form, title='Add a Product', categories=categories)


@app.route('/updateproduct/<int:id>', methods=['GET', 'POST'])
def updateproduct(id):
    form = Addproducts(request.form)
    product = Addproduct.query.get_or_404(id)
    categories = Category.query.all()
    category = request.form.get('category')
    if request.method == "POST":
        product.name = form.name.data
        product.price = form.price.data
        product.discount = form.discount.data
        product.stock = form.stock.data
        product.desc = form.discription.data
        product.category_id = category
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path,
                          "static/images/" + product.image_1))
                product.image_1 = photos.save(request.files.get(
                    'image_1'), name=secrets.token_hex(10) + ".")
            except:
                product.image_1 = photos.save(request.files.get(
                    'image_1'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path,
                          "static/images/" + product.image_2))
                product.image_2 = photos.save(request.files.get(
                    'image_2'), name=secrets.token_hex(10) + ".")
            except:
                product.image_2 = photos.save(request.files.get(
                    'image_2'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path,
                          "static/images/" + product.image_3))
                product.image_3 = photos.save(request.files.get(
                    'image_3'), name=secrets.token_hex(10) + ".")
            except:
                product.image_3 = photos.save(request.files.get(
                    'image_3'), name=secrets.token_hex(10) + ".")

        flash('The product was updated.', 'success')
        db.session.commit()
        return redirect(url_for('admin'))
    form.name.data = product.name
    form.price.data = product.price
    form.discount.data = product.discount
    form.stock.data = product.stock
    form.discription.data = product.desc
    category = product.category.name
    return render_template('products/addproduct.html', form=form, title='Update Product', getproduct=product)


@app.route('/deleteproduct/<int:id>', methods=['POST'])
def deleteproduct(id):
    product = Addproduct.query.get_or_404(id)
    if request.method == "POST":
        try:
            os.unlink(os.path.join(current_app.root_path,
                      "static/images/" + product.image_1))
            os.unlink(os.path.join(current_app.root_path,
                      "static/images/" + product.image_2))
            os.unlink(os.path.join(current_app.root_path,
                      "static/images/" + product.image_3))
        except Exception as e:
            print(e)
        db.session.delete(product)
        db.session.commit()
        flash(f"The product '{product.name}' was delete from your database.", 'success')
        return redirect(url_for('admin'))
    flash(f'Can not delete the product', 'danger')
    return redirect(url_for('admin'))

@app.route('/addauthor', methods=['GET', 'POST'])
def addauthor():
    if request.method == "POST":
        getauthor = request.form.get('author')
        author = Author(name=getauthor)
        db.session.add(author)
        flash(f"The author '{author}' was added to your database.", 'success')
        db.session.commit()
        return redirect(url_for('addauthor'))
    return render_template('products/addauthor.html', title='Add author', authors=authors())

@app.route('/authors/<int:id>')
def get_author(id):
    page = request.args.get('page', 1, type=int)
    get_author = Author.query.filter_by(id=id).first_or_404()
    product = Addproduct.query.all()
    get_author_product = product.authors.all().paginate(page=page, per_page=8)
    return render_template('products/index.html', get_author_product=get_author_product, get_author=get_author, authors=authors())

@app.route('/update_author/<int:id>', methods=['GET', 'POST'])
def update_author(id):
    if 'email' not in session:
        flash('Login your account, thanks.', 'danger')
        return redirect(url_for('login'))
    update_author = Author.query.get_or_404(id)
    author = request.form.get('author')
    if request.method == "POST":
        update_author.name = author
        flash(
            f'The author {update_author.name} was changed to {author}', 'success')
        db.session.commit()
        return redirect(url_for('authors'))
    author = update_author.name
    return render_template('products/addauthor.html', title='Update Author', update_author=update_author)


@app.route('/delete_author/<int:id>', methods=['GET', 'POST'])
def delete_author(id):
    author = Author.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(author)
        flash(
            f"The author {author.name} was deleted from your database", "success")
        db.session.commit()
        return redirect(url_for('admin'))
    flash(
        f"The author {author.name} can't be  deleted from your database", "warning")
    return redirect(url_for('admin'))
