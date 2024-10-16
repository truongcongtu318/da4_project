ecommerce_project/
│
├── app/
│   ├── __init__.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   ├── cart.py
│   │   └── review.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── user_routes.py
│   │   ├── product_routes.py
│   │   ├── order_routes.py
│   │   ├── cart_routes.py
│   │   └── review_routes.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user_schema.py
│   │   ├── product_schema.py
│   │   ├── order_schema.py
│   │   ├── cart_schema.py
│   │   └── review_schema.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── product_service.py
│   │   ├── order_service.py
│   │   ├── cart_service.py
│   │   └── review_service.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py
│       └── decorators.py
│
├── migrations/
│   ├── versions/
│   ├── alembic.ini
│   ├── env.py
│   └── script.py.mako
│
├── config.py
├── requirements.txt
└── run.py