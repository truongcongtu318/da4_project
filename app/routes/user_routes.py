from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.schemas import user_schema, users_schema, logs_schema, reset_password_schema
from app.services.user_service import UserService
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token, get_jwt, jwt_required, get_jwt_identity
from . import user_bp

#Refresh token
@user_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token), 200

# Xác thực và Đăng nhập
@user_bp.route('/register', methods=['POST'])
def register():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400
    try:
        data = user_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422

    user = UserService.create_user(data)
    return jsonify(user_schema.dump(user)), 201

@user_bp.route('/login', methods=['POST'])
def login():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400
    
    email = json_data.get('email')
    password = json_data.get('password')
    
    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    user = UserService.authenticate_user(email, password)
    if user:
        access_token = create_access_token(identity=user.id, additional_claims={'username': user.username})
        refresh_token = create_refresh_token(identity=user.id, additional_claims={'username': user.username})
        return jsonify(access_token=access_token,refresh_token=refresh_token), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

@user_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    UserService.add_token_to_blocklist(jti)
    return jsonify({'message': 'Logged out successfully'}), 200

@user_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'message': 'Email is required'}), 400
    user, message = UserService.forgot_password(email)
    if user:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'message': message}), 404

@user_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    try:
        data = reset_password_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    user = UserService.verify_reset_token(token)
    if not user:
        return jsonify({'message': 'Token is invalid or expired'}), 400

    message = UserService.reset_password(user, data['new_password'])
    return jsonify({'message': message}), 200

@user_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    # Thực hiện logic xác thực email
    return jsonify({'message': 'Email is verified'}), 200

# Quản lý thông tin người dùng
@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = UserService.get_user_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify(user_schema.dump(user)), 200

@user_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    json_data = request.get_json()
    if not json_data.get('current_password') or not json_data.get('new_password'):
        return jsonify({'message': 'Current password and new password are required'}), 400
    user_id = get_jwt_identity()
    user = UserService.get_user_by_id(user_id)
    if len(json_data.get('new_password')) < 6:
        return jsonify({'message': 'Password must be at least 6 characters'}), 400
    if not user:
        return jsonify({'message': 'User not found'}), 404
    success, message = UserService.change_password(user, json_data.get('current_password'), json_data.get('new_password'))
    
    if success:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'message': message}), 400

# Quản lý người dùng (cho admin)
@user_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    users = UserService.get_all_users()
    return jsonify(users_schema.dump(users)), 200

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = UserService.get_user_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify(user_schema.dump(user)), 200

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    user = UserService.get_user_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400
    try:
        data = user_schema.load(json_data, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 422
    
    updated_user = UserService.update_user(user, data)
    return jsonify(user_schema.dump(updated_user)), 200

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    user = UserService.get_user_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    UserService.delete_user(user)
    return jsonify({'message': 'User deleted'}), 204

# Logs và hoạt động người dùng
@user_bp.route('/users/<int:user_id>/logs', methods=['GET'])
@jwt_required()
def get_user_logs(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    logs = UserService.get_user_logs(user_id)
    return jsonify(logs_schema.dump(logs)), 200

