from flask import Flask, render_template, redirect, request, flash, make_response
from flask_ngrok import run_with_ngrok
from flask_restful import abort
from requests import session

import shop_api
from data import db_session
from data.cart import Cart
from data.comments import Comment
from data.products import Product
from data.users import User
from data.category import Category
from forms.CommentForm import CommentForm
from forms.LoginForm import LoginForm
from forms.ProductForm import ProductForm
from forms.RegisterForm import RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__)
#run_with_ngrok(app)
app.register_blueprint(shop_api.blueprint)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    db_sess = db_session.create_session()
    products = db_sess.query(Product)
    cart = [(i.product, i.user) for i in db_sess.query(Cart).all()]
    users = db_sess.query(User)
    return render_template("index.html", products=products, cart=cart, users=users, title="Купи-продай")


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


@app.route('/help')
def helping():
    return render_template('help.html', title='Инструкция по применению!')


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


@app.route('/user/<int:user_id>', methods=["GET", "POST"])
def user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    comments = session.query(Comment).filter(Comment.receiver_id == user_id)
    products = session.query(Product).filter(Product.user_id == user_id)
    return render_template('user.html', user=user, title=f"Пользователь {user.name}",
                           products=products, comments=comments)


@app.route('/userava/<int:user_id>')
def userava(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    img = user.getAvatar(app)
    if not img:
        return ""
    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        session = db_session.create_session()
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                user = session.query(User).get(current_user.id)
                user.avatar = img
                session.commit()
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")
    return redirect(f'/user/{current_user.id}')


@app.route('/product', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()
    if not current_user.is_authenticated:
        return redirect('/')
    session = db_session.create_session()
    if form.validate_on_submit():
        category = form.category.data
        category_id = session.query(Category).filter(Category.title == category).first().id
        product = Product(
            title=form.title.data,
            price=form.price.data,
            description=form.description.data,
            user_id=current_user.id,
            category=category_id
        )
        session.add(product)
        session.commit()
        return redirect(f'/user/{current_user.id}')
    return render_template('add_product.html', title='Добавление товара', form=form, categoryes=session.query(Category).all())


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
            author_id=current_user.id,
            receiver_id=user_id,
            context=form.context.data
        )
        session.add(comment)
        session.commit()
        return redirect(f'/user/{user_id}')
    return render_template('add_comment.html', title='Добавление комментария', form=form)


@app.route('/comment_delete/<int:comm_id>', methods=['GET', 'POST'])
@login_required
def comment_delete(comm_id):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).filter(Comment.id == comm_id).first()
    user = comment.receiver_id
    if not comment:
        abort(404)
    db_sess.delete(comment)
    db_sess.commit()
    return redirect(f'/user/{user}')

@app.route('/comment_edit/<int:comm_id>', methods=['GET', 'POST'])
@login_required
def comment_edit(comm_id):
    form = CommentForm()
    if not current_user.is_authenticated:
        return redirect('/')
    if form.validate_on_submit():
        session = db_session.create_session()
        comment = session.query(Comment).filter(Comment.id == comm_id).first()
        comment.context = form.context.data
        session.commit()
        return redirect(f'/user/{comment.receiver_id}')
    return render_template('edit_comment.html', title='Изменение комментария', form=form)

@app.route('/money/<int:user_id>')
def money(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    user.money = int(user.money - user.money * 0.5) if user.money < 0 else int((user.money + 1) * 1.2)
    session.commit()
    return render_template('money.html', user=user, title=f"Дьенки")


@app.route('/buy/<int:product_id>')
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


@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    session = db_session.create_session()
    product = session.query(Product).get(product_id)
    user = session.query(User).get(current_user.id)
    cart = Cart(user=user.id, product=product.id)
    session.add(cart)
    session.commit()
    return redirect("/")


@app.route('/cart/<int:user_id>')
def cart(user_id):
    session = db_session.create_session()
    cart = session.query(Cart).filter(Cart.user == user_id).all()
    products = [session.query(Product).filter(Product.id == i.product).first() for i in cart]
    user = session.query(User).filter(User.id == user_id).one()
    summ = sum([i.price for i in products])
    return render_template("cart.html", title="Корзинка", products=products, money=user.money, summ=summ)


@app.route('/buy_cart/<int:user_id>')
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

def main():
    app.run()


if __name__ == '__main__':
    db_session.global_init("db/shop.db")
    main()
