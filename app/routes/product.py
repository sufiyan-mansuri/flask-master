import os 
from flask import Blueprint, request, jsonify, current_app, url_for
from werkzeug.utils import secure_filename
from app import db
from app.models.product import Product
from app.models.user import User
from app.forms.product import ProductForm
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

product_bp = Blueprint('products', __name__)

@product_bp.route('/', methods=['POST'])
@jwt_required()
def create_product():
    data = request.form.to_dict()
    form = ProductForm()

    if 'image' in request.files:
        form.image.data = request.files['image']

    if form.validate_on_submit():
        if form.image.data: 
            filname = secure_filename(form.image.data.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filname)
            form.image.data.save(filepath)
            image_path = filepath
        else: 
            image_path = None
        
        current_user = get_jwt_identity()
        owner = User.query.filter_by(username=current_user).first()

        new_product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            category=form.category.data,
            is_available=form.is_available.data,
            image_path=image_path,
            owner=owner,
            created_at=datetime.utcnow()
        )

        db.session.add(new_product)
        db.session.commit()
        return jsonify({"message": "Product created successfully"}), 201
    
    return jsonify({"errors": form.errors}), 400

@product_bp.route('/', methods=['GET'])
def get_all_products():
    products = Product.query.all()
    products_list = []
    for product in products:
        products_list.append({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "category": product.category,
            "is_available": product.is_available,
            "image_url": url_for('static', filename=product.image_path) if product.image_path else None,
            "created_at": product.created_at.isoformat(),
            "owner_username": product.owner.username
        })
    return jsonify(products_list), 200

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "category": product.category,
        "is_available": product.is_available,
        "image_url": url_for('static', filename=product.image_path) if product.image_path else None,
        "created_at": product.created_at.isoformat(),
        "owner_username": product.owner.username
    }), 200

@product_bp.route('/<int:product_id>', methods=['PATCH'])
@jwt_required()
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    current_user = get_jwt_identity()

    if product.owner.username != current_user:
        return jsonify({"message": "You are not authorized to update this product"}), 403

    data = request.form.to_dict()
    form = ProductForm()
    
    if 'image' in request.files:
        form.image.data = request.files['image']

    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = float(data['price'])
    if 'category' in data:
        product.category = data['category']
    if 'is_available' in data:
        product.is_available = data['is_available'].lower() in ['true', '1', 't']

    if 'image' in request.files:
        filename = secure_filename(form.image.data.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        form.image.data.save(filepath)
        if product.image_path and os.path.exists(product.image_path):
            os.remove(product.image_path)
        product.image_path = filepath
    
    db.session.commit()
    return jsonify({"message": "Product updated successfully"}), 200

@product_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Delete a product."""
    product = Product.query.get_or_404(product_id)
    current_user = get_jwt_identity()

    if product.owner.username != current_user:
        return jsonify({"message": "You are not authorized to delete this product"}), 403

    if product.image_path and os.path.exists(product.image_path):
        os.remove(product.image_path)
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"}), 200