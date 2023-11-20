from sqlalchemy.orm import relationship
from app import db
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, DateTime, null
import enum
from datetime import datetime

# Ten reference : ten entity
# backref : ten bien backref nam ben entity so huu , khi khai bao entity bi so huu , se dung backref


class UserRoleEnum(enum.Enum):
    BENH_NHAN = 1
    ADMIN = 2
    BAC_SI = 3
    Y_TA = 4


class BenhNhan(db.Model):
    __tablename__ = 'benhnhan'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_benhnhan = Column(db.String(50), nullable=False)
    sdt = Column(String(50), nullable=False)
    user_role = Column(Enum(UserRoleEnum), default=UserRoleEnum.BENH_NHAN)
    chitiet_benhnhan = relationship('ChiTietBenhNhan',backref="benhnhanBr")
    danhsachkhambenh = relationship('DanhSachKhamBenh',backref="dskbBrbenhnhan")

    def __str__(self):  # Sử dụng __str__ để in ra tên khi sử dụng đối tượng BenhNhan
        return f"BenhNhan(ten_benhnhan={self.ten_benhnhan}, sdt={self.sdt})"


class ChiTietBenhNhan(db.Model):
    __tablename__ = 'chitiet_benhnhan'

    id = Column(Integer, primary_key=True, autoincrement=True)
    gioitinh = Column(String(50), nullable=False)
    ngaysinh = Column(DateTime, nullable=False)
    benhnhan_id = db.Column(Integer, ForeignKey(BenhNhan.id), unique=True)
    diachi = relationship('Address',backref="addressBr")
    bhyt = relationship('BHYT',backref="bhytBr")
    cmnd = relationship('CMND',backref="cmndBr")
    favor = relationship('Favor',backref="favorBr")


    def __str__(self):
        return self.name

class LichKham(db.Model):
    __tablename__ = 'lichkham'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ngaykham = Column(DateTime, nullable=False)
    danhsachkhambenh = relationship('DanhSachKhamBenh',backref="dskbBrlichkham")
    danhsachdangkikhambenh = relationship('DanhSachDangKiKhamBenh',backref="dsdkkbBrlichkham")


    def __str__(self):
        return self.name

class DanhSachKhamBenh(db.Model):
    __tablename__ = 'danhsachkhambenh'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(Integer, ForeignKey(BenhNhan.id))
    lichkham_id = db.Column(Integer,ForeignKey(LichKham.id))

    def __str__(self):
        return self.name


class Address(db.Model):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_diachi = Column(String(200), nullable=False)
    chitiet_benhnhan_id = Column(Integer, ForeignKey(ChiTietBenhNhan.id))

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


class Favor(db.Model):
    __tablename__ = 'favor'

    id = Column(Integer, primary_key=True, autoincrement=True)
    mongmuon = Column(String(200), nullable=False)
    chitiet_benhnhan_id = Column(Integer, ForeignKey(ChiTietBenhNhan.id), unique=True)

    def __str__(self):
        return self.name


class DanhSachDangKiKhamBenh(db.Model):
    __tablename__ = 'danhsachdangkikhambenh'

    id = Column(Integer, primary_key=True, autoincrement=True)
    hoten = Column(db.String(50), nullable=False)
    sdt = Column(db.String(20), nullable=False)
    gioitinh = Column(db.String(5), nullable=False)
    ngaysinh = Column(DateTime, nullable=False)

    diachi_temp = relationship('Address_temp', backref="addressBr_temp")
    bhyt_temp = relationship('BHYT_temp', backref="bhytBr_temp")
    cmnd_temp = relationship('CMND_temp', backref="cmndBr_temp")
    favor_temp = relationship('Favor_temp', backref="favorBr_temp")
    lichkham_id = db.Column(Integer,ForeignKey(LichKham.id))


class Address_temp(db.Model):
        __tablename__ = 'address_temp'

        id = Column(Integer, primary_key=True, autoincrement=True)
        ten_diachi = Column(String(200), nullable=False)
        danhsachdangkikhambenh_id = Column(Integer, ForeignKey(DanhSachDangKiKhamBenh.id))

        def __str__(self):
            return self.name

class BHYT_temp(db.Model):
        __tablename__ = 'bhyt_temp'

        id = Column(Integer, primary_key=True, autoincrement=True)
        so_bhyt = Column(String(20), nullable=False)
        danhsachdangkikhambenh_id = Column(Integer, ForeignKey(DanhSachDangKiKhamBenh.id))

        def __str__(self):
            return self.name

class CMND_temp(db.Model):
        __tablename__ = 'cmnd_temp'

        id = Column(Integer, primary_key=True, autoincrement=True)
        so_cmnd = Column(String(20), nullable=False)
        danhsachdangkikhambenh_id = Column(Integer, ForeignKey(DanhSachDangKiKhamBenh.id))

        def __str__(self):
            return self.name

class Favor_temp(db.Model):
        __tablename__ = 'favor_temp'

        id = Column(Integer, primary_key=True, autoincrement=True)
        mongmuon = Column(String(200),nullable=True)
        danhsachdangkikhambenh_id = Column(Integer, ForeignKey(DanhSachDangKiKhamBenh.id))

        def __str__(self):
            return self.name


if __name__ == "__main__":
    from app import app

    with app.app_context():
        db.create_all()
