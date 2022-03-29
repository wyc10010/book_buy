from wtforms import Form, StringField, TextAreaField, PasswordField,SubmitField,validators, ValidationError, IntegerField, DateField
from flask_wtf.file import FileRequired,FileAllowed, FileField
from flask_wtf import FlaskForm
from .model import Register, Coupon

class CustomerRegisterForm(FlaskForm):
    name = StringField('Name')
    username = StringField('Username', [validators.DataRequired()])
    email = StringField('Email', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired(), validators.EqualTo('confirm', message=' Both password must match! ')])
    confirm = PasswordField('Repeat Password', [validators.DataRequired()])
    contact = StringField('Phone', [validators.DataRequired()])
    zipcode = StringField('Code', [validators.DataRequired()])
    address = StringField('Address', [validators.DataRequired()])
    profile = FileField('Profile', validators=[FileAllowed(['jpg','png','jpeg','gif'], 'Image only please')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        if Register.query.filter_by(username=username.data).first():
            raise ValidationError("This username is already in use!")
        
    def validate_email(self, email):
        if Register.query.filter_by(email=email.data).first():
            raise ValidationError("This email address is already in use!")

class CustomerLoginFrom(FlaskForm):
    email = StringField('Email', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])


class CouponForm(FlaskForm):
    coupon_name = StringField('Coupon Name')
    type = StringField('Type (shipping, seasonings, special event)')
    coupon_discount = IntegerField('Coupon Discount (%, NT)', default=0)
    coupon_limit_discount = IntegerField('Coupon Limit Discount (NT)', default=0)
    quantity = IntegerField('Coupon Quantity', default=0)
    start_date = DateField('Start Date (MM/DD/YYYY)', format='%m/%d/%Y')
    end_date = DateField('End Date (MM/DD/YYYY)', format='%m/%d/%Y')

    def validate_coupon(self, coupon_name):
        if Coupon.query.filter_by(coupon_name=coupon_name.data).first():
            raise ValidationError("This coupon is already exist!")

class OrderCouponForm(FlaskForm):
    order_coupon_name = StringField('Coupon Name:')