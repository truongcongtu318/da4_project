from flask import Blueprint

user_bp = Blueprint('user', __name__)
product_bp = Blueprint('product', __name__)
order_bp = Blueprint('order', __name__)
cart_bp = Blueprint('cart', __name__)

from . import user_routes
from . import product_routes
from . import order_routes
from . import cart_routes