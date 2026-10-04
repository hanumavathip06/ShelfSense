from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import Category
from app.schemas import category_schema, categories_schema
from app.extensions import db
from app.utils.auth import requires_permission, Permission
from app.utils.errors import api_error

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('', methods=['GET'])
@jwt_required()
@requires_permission(Permission.DASHBOARD_VIEW)
def get_categories():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    pagination = Category.query.paginate(page=page, per_page=limit, error_out=False)
    return jsonify({
        'items': categories_schema.dump(pagination.items),
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages
    })

@categories_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
@requires_permission(Permission.DASHBOARD_VIEW)
def get_category(id):
    category = Category.query.get(id)
    if not category:
        return api_error("Category not found", 404)
    return jsonify(category_schema.dump(category))

@categories_bp.route('', methods=['POST'])
@jwt_required()
@requires_permission(Permission.INVENTORY_EDIT)
def create_category():
    data = request.get_json()
    errors = category_schema.validate(data)
    if errors:
        return api_error(str(errors), 400)
    if Category.query.filter_by(name=data['name']).first():
        return api_error("Category already exists", 409)
    category = Category(name=data['name'])
    db.session.add(category)
    db.session.commit()
    return jsonify(category_schema.dump(category)), 201

@categories_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@requires_permission(Permission.INVENTORY_EDIT)
def update_category(id):
    category = Category.query.get(id)
    if not category:
        return api_error("Category not found", 404)
    data = request.get_json()
    errors = category_schema.validate(data, partial=True)
    if errors:
        return api_error(str(errors), 400)
    if 'name' in data:
        existing = Category.query.filter_by(name=data['name']).first()
        if existing and existing.id != id:
            return api_error("Category name already exists", 409)
        category.name = data['name']
    db.session.commit()
    return jsonify(category_schema.dump(category))

@categories_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@requires_permission(Permission.INVENTORY_EDIT)
def delete_category(id):
    category = Category.query.get(id)
    if not category:
        return api_error("Category not found", 404)
    db.session.delete(category)
    db.session.commit()
    return '', 204
