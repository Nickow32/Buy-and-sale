import flask
from flask import jsonify, request

from data import db_session
from data.products import Product
from data.users import User

blueprint = flask.Blueprint(
    'shop_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/user/<int:user_id>', methods=["GET"])
def get_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return jsonify({"error": "User not found"})
    return jsonify(
        {
            "user": [user.to_dict(only=("name", "email", "phone", "money"))]
        }
    )


@blueprint.route('/api/user/<int:user_id>', methods=["DELETE"])
def delete_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return jsonify({"error": "User not found"})
    session.delete(user)
    session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/user/<int:user_id>', methods=["PUT"])
def change_user(user_id):
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['name', 'phone', 'email']):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return jsonify({"error": "User not found"})
    user.name = request.json['name']
    user.phone = request.json['phone']
    user.email = request.json['email']
    session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/user', methods=["GET"])
def get_users():
    session = db_session.create_session()
    users = session.query(User).all()
    return jsonify(
        {
            "users": [item.to_dict(only=("name", "email", "phone", "money")) for item in users]
        }
    )


@blueprint.route('/api/user', methods=["POST"])
def post_user():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['name', 'phone', 'email', 'hashed_password', "money"]):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    user = User(
        name=request.json['name'],
        phone=request.json['phone'],
        email=request.json['email'],
        hashed_password=request.json['hashed_password'],
        money=request.json['money']
    )
    session.add(user)
    session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/product/<int:product_id>', methods=["GET"])
def get_product(product_id):
    session = db_session.create_session()
    product = session.query(Product).get(product_id)
    if not product:
        return jsonify({"error": "Product not found"})
    return jsonify(
        {
            "user": [product.to_dict(only=("title", "description", "price"))]
        }
    )


@blueprint.route('/api/product/<int:product_id>', methods=["PUT"])
def change_product(product_id):
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ["title", "description", "price", "user_id"]):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    product = session.query(Product).get(product_id)
    if not product:
        return jsonify({"error": "Product not found"})
    product.name = request.json['title']
    product.phone = request.json['description']
    product.email = request.json['price']
    product.email = request.json['user_id']
    session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/product/<int:product_id>', methods=["DELETE"])
def delete_product(product_id):
    session = db_session.create_session()
    product = session.query(Product).get(product_id)
    if not product:
        return jsonify({"error": "Product not found"})
    session.delete(product)
    session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/product', methods=["GET"])
def get_products():
    session = db_session.create_session()
    users = session.query(Product).all()
    return jsonify(
        {
            "products": [item.to_dict(only=("title", "description", "price")) for item in users]
        }
    )


@blueprint.route('/api/product', methods=["POST"])
def post_product():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ["title", "description", "price"]):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    product = Product(
        title=request.json['title'],
        description=request.json['description'],
        price=request.json['price']
    )
    session.add(product)
    session.commit()
    return jsonify({'success': 'OK'})