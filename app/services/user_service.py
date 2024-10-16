from flask import current_app, jsonify, url_for
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from app.models.user import User, Log, TokenBlocklist
from app import db, mail
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity
from datetime import timedelta
from flask_mail import Message
import secrets

class UserService:
    # Các phương thức truy vấn người dùng
    @staticmethod
    def get_all_users():
        return User.query.all()

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()

    # Các phương thức quản lý người dùng
    @staticmethod
    def create_user(data):
        user = User(username=data['username'], email=data['email'], address=data['address'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()

        log = Log(user_id=user.id, action='User created')
        db.session.add(log)
        db.session.commit()

        return user

    @staticmethod
    def update_user(user, data):
        for key, value in data.items():
            if key == 'password':
                user.set_password(value)
            else:
                setattr(user, key, value)
        
        db.session.commit()

        log = Log(user_id=user.id, action='User updated')
        db.session.add(log)
        db.session.commit()

        return user

    @staticmethod
    def delete_user(user):
        user_id = user.id
        db.session.delete(user)
        db.session.commit()

        log = Log(user_id=user_id, action='User deleted')
        db.session.add(log)
        db.session.commit()

    # Phương thức xử lý nhật ký
    @staticmethod
    def get_user_logs(user_id):
        return Log.query.filter_by(user_id=user_id).all()

    # Các phương thức xác thực và quản lý phiên đăng nhập
    @staticmethod
    def authenticate_user(email, password):
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return user
        return None
    
    @staticmethod
    def add_token_to_blocklist(jti):
        token = TokenBlocklist(jti=jti)
        db.session.add(token)
        db.session.commit()

    @staticmethod
    def is_token_revoked(jwt_payload):
        jti = jwt_payload['jti']
        token = TokenBlocklist.query.filter_by(jti=jti).first()
        return token is not None
    

    # Các phương thức quản lý mật khẩu
    @staticmethod
    def generate_reset_token(user):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return serializer.dumps(user.id, salt='reset-password-salt')

    @staticmethod
    def verify_reset_token(token, expiration=3600):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            user_id = serializer.loads(
                token,
                salt='reset-password-salt',
                max_age=expiration
            )
        except (SignatureExpired, BadSignature):
            return None
        return User.query.get(user_id)
    
    @staticmethod
    def change_password(user, current_password, new_password):
        if not user.check_password(current_password):
            return False, 'Current password is incorrect'
        user.set_password(new_password)
        db.session.commit()
        log = Log(user_id=user.id, action='Password changed')
        db.session.add(log)
        db.session.commit()
        return True, 'Password changed successfully'
    
    @staticmethod
    def forgot_password(email):
        user = User.query.filter_by(email=email).first()
        if not user:
            return None, 'User not found with this email'
        
        token = UserService.generate_reset_token(user)
        reset_url = url_for('user.reset_password', token=token, _external=True)
        
        try:
            msg = Message('Reset Password', 
                          sender=current_app.config['MAIL_DEFAULT_SENDER'], 
                          recipients=[email])
            msg.body = f'''To reset your password, please click the link below:

{reset_url}

This link will expire in 1 hour.
If you did not request a password reset, please ignore this email.'''
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f'Not send email reset password: {str(e)}')
            return None, 'Not send email reset password'
        
        log = Log(user_id=user.id, action='Send email reset password')
        db.session.add(log)
        db.session.commit()
        
        return user, 'Send email reset password'
    
    @staticmethod
    def reset_password(user, new_password):
        user.set_password(new_password)
        db.session.commit()

        log = Log(user_id=user.id, action='Password reset')
        db.session.add(log)
        db.session.commit()

        return "Password reset successfully"

