from .user_schema import ResetPasswordSchema, UserSchema, LogSchema

user_schema = UserSchema()
users_schema = UserSchema(many=True)

log_schema = LogSchema()
logs_schema = LogSchema(many=True)

reset_password_schema = ResetPasswordSchema()
