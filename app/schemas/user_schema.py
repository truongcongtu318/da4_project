from flask_jwt_extended import get_jwt_identity
from marshmallow import Schema, ValidationError, fields, validate, validates

from app.models.user import User

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))
    role = fields.Str(validate=validate.OneOf(['user', 'admin']), default='user')
    address = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    
    @validates('username')
    def validate_username(self, value):
        try:
            current_user_id = get_jwt_identity()
        except RuntimeError:
            current_user_id = None
        existing_user = User.query.filter_by(username=value).first()
        if existing_user and existing_user.id != current_user_id:
            raise ValidationError('Username already exists.')

    @validates('email')
    def validate_email(self, value):
        try:
            current_user_id = get_jwt_identity()
        except RuntimeError:
            current_user_id = None
        existing_user = User.query.filter_by(email=value).first()
        if existing_user and existing_user.id != current_user_id:
            raise ValidationError('Email already exists.')

class LogSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    action = fields.Str(required=True)
    details = fields.Str()
    timestamp = fields.DateTime(dump_only=True)

class ResetPasswordSchema(Schema):
    new_password = fields.Str(required=True, validate=validate.Length(min=6))
    

# user_schema = UserSchema()
# users_schema = UserSchema(many=True)

# log_schema = LogSchema()
# log_schemas = LogSchema(many=True)

# reset_password_schema = ResetPasswordSchema()