from app import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    shipping_id = db.Column(db.Integer, db.ForeignKey('shipping.id'))
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'))
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='orders')
    shipping = db.relationship('Shipping', back_populates='order')
    coupon = db.relationship('Coupon', back_populates='orders')
    payment = db.relationship('Payment', back_populates='order')
    order_items = db.relationship('OrderItem', back_populates='order')

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    order = db.relationship('Order', back_populates='order_items')
    product = db.relationship('Product', back_populates='order_items')

class Shipping(db.Model):
    __tablename__ = 'shipping'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), nullable=False)
    shipping_method = db.Column(db.String(50), nullable=False)
    tracking_number = db.Column(db.String(50))
    status = db.Column(db.String(20), nullable=False)

    order = db.relationship('Order', back_populates='shipping', uselist=False)

class Payment(db.Model):
    __tablename__ = 'payment'
    id = db.Column(db.Integer, primary_key=True)
    payment_method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    transaction_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship('Order', back_populates='payment', uselist=False)

class Coupon(db.Model):
    __tablename__ = 'coupons'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    discount = db.Column(db.Float, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    min_purchase = db.Column(db.Float)

    orders = db.relationship('Order', back_populates='coupon')