from app import db

from datetime import datetime

class Cart(db.Model):
    __tablename__ = 'carts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='cart')
    items = db.relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cart = db.relationship('Cart', back_populates='items')
    product = db.relationship('Product', back_populates='cart_items')
 
 