import flask
from flask import render_template, redirect
from flask_login import current_user

from data import db_session
from data.cart import Cart
from data.comments import Comment
from data.products import Product
from data.users import User

blueprint = flask.Blueprint(
    'shop_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/user/<int:user_id>')
def get_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    products = session.query(Product).filter(Product.user_id == user_id)
    comments = session.query(Comment).filter(Comment.receiver == user_id)
    return render_template('user.html', user=user, title=f"Пользователь {user.name}",
                           products=products, comments=comments)


@blueprint.route('/money/<int:user_id>')
def money(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    user.money += 500
    session.commit()
    return render_template('money.html', user=user, title=f"Дьенки")


@blueprint.route('/buy/<int:product_id>')
def buy(product_id):
    session = db_session.create_session()
    product = session.query(Product).get(product_id)
    user = session.query(User).get(product.user_id)
    user2 = session.query(User).get(current_user.id)
    user.money += product.price
    user2.money -= product.price
    product.user_id = current_user.id
    session.commit()
    return render_template('buy.html', title=f"Поздравляем с покупкой!")


@blueprint.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    session = db_session.create_session()
    product = session.query(Product).get(product_id)
    user = session.query(User).get(current_user.id)
    cart = Cart(user=user.id, product=product.id)
    session.add(cart)
    session.commit()
    return redirect("/")


@blueprint.route('/cart/<int:user_id>')
def cart(user_id):
    session = db_session.create_session()
    cart = session.query(Cart).filter(Cart.user == user_id).all()
    products = [session.query(Product).filter(Product.id == i.product).first() for i in cart]
    summ = sum([i.price for i in products])
    return render_template("cart.html", title="Корзинка", products=products, summ=summ)


@blueprint.route('/buy_cart/<int:user_id>')
def buy_cart(user_id):
    session = db_session.create_session()
    user = session.query(User).get(current_user.id)
    cart = session.query(Cart).filter(Cart.user == user_id).all()
    products = [session.query(Product).filter(Product.id == i.product).first() for i in cart]
    for i in products:
        user.money -= i.price
        user2 = session.query(User).get(i.user_id)
        user2.money += i.price
        i.user_id = current_user.id
        product = session.query(Cart).filter(Cart.user == user_id, Cart.product == i.id).first()
        session.delete(product)
        session.commit()
    return render_template("buy.html", title="Поздравляем с покупкой!")
