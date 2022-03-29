from sqlalchemy.orm import backref
from shop import db
from datetime import datetime

product_author = db.Table('product_author',
    db.Column('product_id', db.Integer, db.ForeignKey('addproduct.id')),
    db.Column('author_id', db.Integer, db.ForeignKey('author.id'))
)

class Addproduct(db.Model):
    __seachbale__ = ['name','desc']
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)

    price = db.Column(db.Numeric(10,2), nullable=False)
    discount = db.Column(db.Integer, default=0)
    stock = db.Column(db.Integer, nullable=False)

    desc = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category',backref=db.backref('categories', lazy=True))

    image_1 = db.Column(db.String(150))
    image_2 = db.Column(db.String(150))
    image_3 = db.Column(db.String(150))

    authors = db.relationship('Author', secondary=product_author, backref=db.backref('addproducts'))

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), unique=True, nullable=False)

    def __repr__(self):
        return '<Catgory %r>' % self.name

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'{self.name}'

db.create_all()