from flask import Blueprint, request, jsonify, url_for
from app import db, revoked_tokens, mail, bcrypt
from app.models import User
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from flask_mail import Message
from datetime import datetime, timedelta
import secrets
from app.forms import RegistrationForm, LoginForm, PasswordResetRequestForm, PasswordResetForm

auth_bp = Blueprint('auth', __name__)

def validate_form_data(form_class, data):
    form = form_class(meta={'csrf': False}) 
    form.process(data=data)
    if form.validate():
        return form, None
    return None, form.errors

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    form, errors = validate_form_data(RegistrationForm, data)

    if errors:
        return jsonify({'errors': errors}), 400

    new_user = User(username=form.username.data, email=form.email.data, password=form.password.data)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    form, errors = validate_form_data(LoginForm, data)

    if errors:
        return jsonify({"errors": errors}), 400

    user = User.query.filter_by(username=form.username.data).first()

    if user and user.check_password(form.password.data):
        access_token = create_access_token(identity=user.username)
        refresh_token = create_refresh_token(identity=user.username)
        return jsonify(access_token=access_token, refresh_token=refresh_token), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401
    
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    revoked_tokens.add(jti)
    return jsonify({'message': 'Successfully logged out'}), 200 

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    return jsonify({"msg": f"Hello, {current_user}! This is a protected route."}), 200

@auth_bp.route('/reset_request', methods=['POST'])
def reset_request():
    data = request.get_json()
    form, errors = validate_form_data(PasswordResetRequestForm, data)

    if errors:
        return jsonify({"errors": errors}), 400

    user = User.query.filter_by(email=form.email.data).first()

    if not user:
        return jsonify({'message': 'Email not found'}), 404
     
    token = secrets.token_urlsafe(32)
    token_expiration = datetime.utcnow() + timedelta(minutes=30)

    user.reset_token = token
    user.token_expiration = token_expiration
    db.session.commit()

    email = Message('Password Reset Request', sender='mansurisufiyan414@gmail.com', recipients=[user.email])
    email.html = f'''<p>To reset your password, <a href="{url_for('auth.reset_password', token=token, _external=True)}">click here</a>.</p>
    <p>If the above link doesn't work, please copy and paste the following URL into your browser:</p>
    <p>{url_for('auth.reset_password', token=token, _external=True)}</p>
    <br>
    <p>If you did not make this request then simply ignore this email and no changes will be made.</p>
    '''
    
    mail.send(email)

    return jsonify({'message': 'Password reset link sent to your email'}), 200

@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    form, errors = validate_form_data(PasswordResetForm, data)

    if errors:
        return jsonify({"errors": errors}), 400

    token = data.get('token')

    user = User.query.filter_by(reset_token=token).first()

    if not user or user.token_expiration < datetime.utcnow():
         return jsonify({"message": "Invalid or expired token"}), 400
    
    if user.check_password(form.password.data):
         return jsonify({"message": "New password cannot be the same as the old password"}), 400
    
    user.password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
    user.reset_token = None
    user.token_expiration = None
    db.session.commit()

    return jsonify({"message": "Password updated successfully"}), 200
