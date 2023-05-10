import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship

from data.db_session import SqlAlchemyBase


class Comment(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    receiver_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    context = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    author = relationship("User", foreign_keys="Comment.author_id")
    receiver = relationship("User", foreign_keys="Comment.receiver_id")