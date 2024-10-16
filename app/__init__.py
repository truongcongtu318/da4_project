import logging
from flask import Flask, request
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, get_jwt, get_jwt_identity, verify_jwt_in_request
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()

# Cấu hình logger
logging.basicConfig(level=logging.DEBUG)  # Đặt mức độ ghi log là DEBUG
logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    
    from app.services.user_service import UserService
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return UserService.is_token_revoked(jwt_payload)

    # Import các model
    from app.models import user, product, order, cart

    # Đăng ký các blueprint ở đây (sẽ thêm sau)
    from app.routes.user_routes import user_bp
    app.register_blueprint(user_bp, url_prefix='/api')

    # Middleware để ghi log thông tin request
    from datetime import datetime

    @app.before_request
    def log_request_info():
        method = request.method
        path = request.path
        user_info = "Anonymous User"  # Mặc định là Anonymous User

        # Lấy tên người dùng từ token nếu có
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Lấy token từ header
            try:
                verify_jwt_in_request() 
                user = get_jwt()
                user_info = f"User{{Id:{user['sub']}, name:{user.get('username')}}}"  # Định dạng thông tin người dùng
            except Exception as e:
                logger.error(f"Error decoding token: {e}")  # Ghi log lỗi khi giải mã token

        # Ghi log với thông tin cần thiết
        logger.info(f"{user_info} - {request.remote_addr} - {method} {request.url}")

    @app.after_request
    def log_response_info(response):
        status_code = response.status_code
        status_descriptions = {
            200: "OK",
            201: "Created",
            202: "Accepted",
            204: "No Content",
            301: "Moved Permanently",
            302: "Found",
            304: "Not Modified",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            408: "Request Timeout",
            409: "Conflict",
            410: "Gone",
            429: "Too Many Requests",
            500: "Internal Server Error",
            501: "Not Implemented",
            502: "Bad Gateway",
            503: "Service Unavailable",
            504: "Gateway Timeout",
        }

        description = status_descriptions.get(status_code, "Unknown Status")
        logger.info(f"Response - Status Code: {status_code} - Description: {description}")

        # Ghi log lỗi nếu status code là 4xx hoặc 5xx
        if status_code >= 400:
            logger.error(f"Error response - Status Code: {status_code} - Description: {description}")

        return response

    return app