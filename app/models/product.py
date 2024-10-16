from app import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship('Category', back_populates='products')
    inventory = db.relationship('Inventory', back_populates='product')
    reviews = db.relationship('Review', back_populates='product')
    cart_items = db.relationship('CartItem', back_populates='product')
    wishlists = db.relationship('Wishlist', back_populates='product')
    order_items = db.relationship('OrderItem', back_populates='product')
    
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)

    products = db.relationship('Product', back_populates='category')

class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    product = db.relationship('Product', back_populates='inventory', uselist=False)

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='reviews')
    product = db.relationship('Product', back_populates='reviews')

class Wishlist(db.Model):
    __tablename__ = 'wishlists'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='wishlists')
    product = db.relationship('Product', back_populates='wishlists')