from sqlalchemy.orm import relationship
from app import db
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum , DateTime
import enum
from datetime import datetime

# Ten reference : ten bang chu ko phai ten cua entity
# backref : ten bien backref nam ben entity so huu , khi khai bao entity bi so huu , se dung backref


class UserRoleEnum(enum.Enum):
    USER = 1
    ADMIN = 2


class BenhNhan(db.Model, UserMixin):
    __tablename__ = 'benhnhan'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)

    user_role = Column(Enum(UserRoleEnum), default=UserRoleEnum.USER)
    chitiet_benhnhan = relationship('ChiTietBenhNhan',backref="benhnhanBr")
    def __str__(self):  # Sử dụng __str__ để in ra tên khi sử dụng đối tượng BenhNhan
        return self.name

class ChiTietBenhNhan(db.Model):
    __tablename__ = 'chitiet_benhnhan'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten = Column(String(50), nullable=False)
    sdt = Column(String(50), nullable=False, unique=True)
    gioitinh = Column(String(50), nullable=False)
    ngaysinh = Column(DateTime, nullable=False)
    user_id = db.Column(Integer, ForeignKey(BenhNhan.id), unique=True)
    email = relationship('Email',backref="emailBr")
    bhyt = relationship('BHYT',backref="bhytBr")
    cmnd = relationship('CMND',backref="cmndBr")


    def __str__(self):
        return self.name
class Email(db.Model):
    __tablename__ = 'email'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_email = Column(String(20), nullable=False, unique=True)
    chitiet_benhnhan_id = Column(Integer, ForeignKey(ChiTietBenhNhan.id), unique=True)

    def __str__(self):
        return self.name


class BHYT(db.Model):
    __tablename__ = 'bhyt'

    id = Column(Integer, primary_key=True, autoincrement=True)
    so_bhyt = Column(String(20), nullable=False, unique=True)
    chitiet_benhnhan_id = Column(Integer, ForeignKey(ChiTietBenhNhan.id), unique=True)

    def __str__(self):
        return self.name

class CMND(db.Model):
    __tablename__ = 'cmnd'

    id = Column(Integer, primary_key=True, autoincrement=True)
    so_cmnd = Column(String(20), nullable=False, unique=True)
    chitiet_benhnhan_id = Column(Integer, ForeignKey(ChiTietBenhNhan.id), unique=True)

    def __str__(self):
        return self.name


if __name__ == "__main__":
    from app import app

    with app.app_context():
        db.create_all()
