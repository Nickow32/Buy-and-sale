from flask import Flask, render_template, redirect, request
from flask_restful import abort

import shop_api
from data import db_session
from data.cart import Cart
from data.comments import Comment
from data.products import Product
from data.users import User
from forms.CommentForm import CommentForm
from forms.LoginForm import LoginForm
from forms.ProductForm import ProductForm
from forms.RegisterForm import RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_ngrok import run_with_ngrok

app = Flask(__name__)
run_with_ngrok(app)
app.register_blueprint(shop_api.blueprint)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    products = db_sess.query(Product)
    cart = [(i.product, i.user) for i in db_sess.query(Cart).all()]
    return render_template("index.html", products=products, cart=cart, title="Купи-продай")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/product', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()
    if not current_user.is_authenticated:
        return redirect('/')
    if form.validate_on_submit():
        product = Product(
            title=form.title.data,
            price=form.price.data,
            description=form.description.data,
            user_id=current_user.id
        )
        session = db_session.create_session()
        session.add(product)
        session.commit()
        return redirect(f'/user/{current_user.id}')
    return render_template('add_product.html', title='Добавление товара', form=form)


@app.route('/product/<int:id>', methods=['GET', 'POST'])
def product(id):
    form = ProductForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        product = db_sess.query(Product).filter(Product.id == id, Product.user == current_user).first()
        if not product:
            return redirect('/')
        if product:
            form.title.data = product.title
            form.price.data = product.price
            form.description.data = product.description
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        product = db_sess.query(Product).filter(Product.id == id, Product.user == current_user).first()
        if product:
            product.title = form.title.data
            product.price = form.price.data
            product.description = form.description.data
            db_sess.commit()
            return redirect(f'/user/{current_user.id}')
        else:
            abort(404)
    return render_template('add_product.html', title='Редактирование товара', form=form)


@app.route('/product_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def product_delete(id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == id, Product.user == current_user).first()
    if not product:
        return redirect('/')
    if product:
        db_sess.delete(product)
        db_sess.commit()
    else:
        abort(404)
    return redirect(f'/user/{current_user.id}')


@app.route('/add_comment/<int:user_id>', methods=['GET', 'POST'])
def add_comment(user_id):
    form = CommentForm()
    if not current_user.is_authenticated:
        return redirect('/')
    if form.validate_on_submit():
        session = db_session.create_session()
        comment = Comment(
            author=current_user.name,
            receiver=user_id,
            context=form.context.data
        )
        session.add(comment)
        session.commit()
        return redirect(f'/user/{user_id}')
    return render_template('add_comment.html', title='Добавление комментария', form=form)


@app.route('/comment_delete/<string:author>', methods=['GET', 'POST'])
@login_required
def comment_delete(author):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).filter(Comment.author == author, Comment.receiver == current_user.id).first()
    if not comment:
        return redirect('/')
    if comment:
        db_sess.delete(comment)
        db_sess.commit()
    else:
        abort(404)
    return redirect(f'/user/{current_user.id}')


def main():
    app.run()


if __name__ == '__main__':
    db_session.global_init("db/shop.db")
    main()
