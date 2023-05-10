import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase


class Category(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'category'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    
    product_ = orm.relation('Product', back_populates='category_')