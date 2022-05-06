from hashlib import md5

import sqlalchemy
from flask import url_for
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from data.db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    phone = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    money = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    avatar = sqlalchemy.Column(sqlalchemy.BLOB, default=None)

    products = orm.relation("Product", back_populates='user')
    comments = orm.relation("Comment", back_populates='user')
    carts = orm.relation("Cart", back_populates='user_')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def getAvatar(self, app):
        img = None
        if not self.avatar:
            try:
                with app.open_resource(app.root_path + '\images\default.png', "rb") as f:
                    img = f.read()
            except FileNotFoundError as e:
                print("Не найден аватар по умолчанию: " + str(e))
        else:
            img = self.avatar
        return img

    def verifyExt(self, filename):
        ext = filename.rsplit('.', 1)[1]
        if ext in ['png', 'jpg', 'jpeg', 'gif']:
            return True
        return False