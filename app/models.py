from sqlalchemy.orm import relationship
from app import db
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, DateTime, Boolean, SmallInteger
import enum
from datetime import datetime
from flask_login import UserMixin


# Ten reference : ten entity
# backref : ten bien backref nam ben entity so huu , khi khai bao entity bi so huu , se dung backref


class UserRoleEnum(enum.Enum):
    BENH_NHAN = 1
    ADMIN = 2
    BAC_SI = 3
    Y_TA = 4
    THU_NGAN = 5


class Manager(db.Model, UserMixin):
    __tablename__ = 'manager'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_quantri = Column(db.String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    gioitinh = Column(String(50), nullable=False)
    cmnd = Column(String(50), nullable=False, unique=True)
    sdt = Column(String(50), nullable=False, unique=True)
    ngaysinh = Column(DateTime, nullable=False)
    hinhanh = Column(String(100),
                     default='https://res.cloudinary.com/diwxda8bi/image/upload/v1703312060/Adorable-animal-cat'
                             '-20787_ebmgss.jpg')
    diachi = Column(String(50), nullable=False)
    user_role = Column(Enum(UserRoleEnum), default=UserRoleEnum.ADMIN)

    def __str__(self):
        return self.name


class BenhNhan(db.Model):
    __tablename__ = 'benhnhan'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_benhnhan = Column(db.String(50), nullable=False)
    user_role = Column(Enum(UserRoleEnum), default=UserRoleEnum.BENH_NHAN)
    chitietbenhnhan = relationship('ChiTietBenhNhan', backref="chitietbenhnhanBrbenhnhan", uselist=False)
    phieukhambenh = db.relationship('PhieuKhamBenh', backref='phieukhambenhBackrefbenhnhan')

    # danhsachkhambenh = relationship('DanhSachKhamBenh', backref="dskbBrbenhnhan")

    def __str__(self):  # Sử dụng __str__ để in ra tên khi sử dụng đối tượng BenhNhan
        return f"BenhNhan(ten_benhnhan={self.ten_benhnhan})"


class ChiTietBenhNhan(db.Model):
    __tablename__ = 'chitietbenhnhan'

    id = Column(Integer, primary_key=True, autoincrement=True)
    gioitinh = Column(String(50), nullable=False)
    sdt = Column(String(50), nullable=False, unique=True)
    ngaysinh = Column(DateTime, nullable=False)
    benhnhan_id = db.Column(Integer, ForeignKey(BenhNhan.id), unique=True, nullable=False)
    diachi = relationship('Address', backref="addressBr")
    bhyt = relationship('BHYT', backref="bhytBr")
    cmnd = relationship('CMND', backref="cmndBr")
    favor = relationship('Favor', backref="favorBr")

    def __str__(self):
        return f"ChiTietBenhNhan(id={self.id} , benhnhan_id={self.benhnhan_id})"


class LichKham(db.Model):
    __tablename__ = 'lichkham'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ngaykham = Column(DateTime, nullable=False)

    #    danhsachkhambenh = relationship('DanhSachKhamBenh', backref="lickkham", lazy=True)

    def __str__(self):
        return f"LichKham(id={self.id}, benhnhan_id={self.ngaykham})"


class DanhSachKhamBenh(db.Model):
    __tablename__ = 'danhsachkhambenh'

    id = Column(Integer, primary_key=True, autoincrement=True)
    stt = db.Column(Integer, nullable=False)
    benhnhan_id = db.Column(Integer, ForeignKey(BenhNhan.id))
    lichkham_id = db.Column(Integer, ForeignKey(LichKham.id))
    lichkham = db.relationship('LichKham', backref='lichKhamBackrefDanhSachKhamBenhs')
    benhnhan = db.relationship('BenhNhan', backref='benhnhanBackrefDanhSachKhamBenhs')

    def __str__(self):
        return f"DanhSachKhamBenh(id={self.id}, benhnhan_id={self.benhnhan_id} , lichkham_id={self.lichkham_id})"


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
    chitiet_benhnhan_id = Column(Integer, ForeignKey(ChiTietBenhNhan.id))

    def __str__(self):
        return self.name


class Config(db.Model):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_config = Column(String(40), nullable=False, unique=True)
    key = Column(String(30), nullable=False, unique=True)
    value = Column(String(30), nullable=False)


class DonViThuoc(db.Model):
    __tablename__ = 'donvithuoc'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_donvithuoc = Column(String(10), nullable=False, unique=True)
    loaithuoc_donvithuoc = db.relationship('LoaiThuoc_DonViThuoc', backref='loaithuoc_donvithuocBackrefDonViThuoc')


class LoaiThuoc(db.Model):
    __tablename__ = 'loaithuoc'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_loaithuoc = Column(String(100), nullable=False, unique=True)
    loaithuoc_donvithuoc = db.relationship('LoaiThuoc_DonViThuoc', backref='loaithuoc_donvithuocBackrefLoaiThuoc')


class LoaiThuoc_DonViThuoc(db.Model):
    __tablename__ = 'loaithuoc_donvithuoc'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    donvithuoc_id = db.Column(db.Integer, db.ForeignKey(DonViThuoc.id))
    loaithuoc_id = db.Column(db.Integer, db.ForeignKey(LoaiThuoc.id))
    giatien = Column(db.Float)
    dslieuluong = db.relationship('DsLieuLuongThuoc', backref='dsLieuLuongBackrefloaithuoc_donvithuoc')


class PhieuKhamBenh(db.Model):
    __tablename__ = 'phieukhambenh'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_nguoikham = Column(String(100), nullable=False)
    sdt = Column(String(100), nullable=False)
    lichkham = db.relationship('LichKham', backref='lichKhamBackrefPhieuKhamBenh')
    dslieuluongthuoc = db.relationship('DsLieuLuongThuoc', backref='dslieuluongthuocBackrefPhieuKhamBenh')
    trieuchung = Column(String(255), nullable=False)
    dudoanbenh = Column(String(255), nullable=False)
    ngaylapphieukham = Column(DateTime, nullable=False)
    lichkham_id = db.Column(Integer, ForeignKey(LichKham.id), nullable=False)
    benhnhan_id = db.Column(Integer, ForeignKey(BenhNhan.id), nullable=False)


class DsLieuLuongThuoc(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    loaithuoc_donvithuoc_id = Column(db.Integer, db.ForeignKey(LoaiThuoc_DonViThuoc.id), nullable=False)
    soluong = db.Column(db.Integer, nullable=False)
    cachdung = Column(String(255), nullable=False)
    phieukhambenh_id = db.Column(Integer, ForeignKey(PhieuKhamBenh.id), nullable=False)


class HoaDonThanhToan(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ngaylaphoadon = Column(DateTime, nullable=False)
    tienkham = Column(Float, nullable=False)
    tienthuoc = Column(Float, nullable=False)
    tongcong = Column(Float, nullable=False)
    trangthai = Column(db.SmallInteger, nullable=False, default=0)
    benhnhan = db.relationship('BenhNhan', backref='benhnhanBackrefhoadonthanhtoan')
    benhnhan_id = db.Column(Integer, ForeignKey(BenhNhan.id), nullable=False)
    phieukhambenh = db.relationship('PhieuKhamBenh', backref='phieukhambenhBackrefhoadonthanhtoan', uselist=False)
    phieukhambenh_id = db.Column(Integer, ForeignKey(PhieuKhamBenh.id), nullable=False)


class MomoPayment(db.Model):
    __tablename__ = 'momopayment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    partnerCode = Column(String(50), nullable=False)
    orderId = Column(String(50), nullable=False, unique=True)
    requestId = Column(String(50), nullable=False)
    amount = Column(String(50), nullable=False)
    orderInfo = Column(String(50), nullable=False)
    orderType = Column(String(50), nullable=False)
    transId = Column(String(50), nullable=False)
    payType = Column(String(50), nullable=False)
    signature = Column(String(150), nullable=False)

    def __str__(self):
        return self.name


if __name__ == "__main__":
    from app import app

    with app.app_context():
        db.create_all()
        import hashlib

        superadmin = Manager(ten_quantri='superadmin'
                             , username='superadmin'
                             , password=str(hashlib.md5('Abc@123'.encode('utf-8')).hexdigest())
                             , gioitinh='other', cmnd="000000000000", sdt='0000000000',
                             ngaysinh=datetime.strptime('2023-11-22 00:00:00', "%Y-%m-%d %H:%M:%S")
                             , hinhanh=None, diachi='diachi', user_role=UserRoleEnum.ADMIN)

        patients_per_day_config = Config(ten_config="Số lượng bệnh nhân tối đa trong 1 ngày", key='patients_per_day',
                                         value='40')
        medical_expenses = Config(ten_config="Tiền khám bệnh trong 1 lần khám", key='medical_expenses', value='100000')

        number_of_per_pack = Config(ten_config="Số viên thuốc của mỗi vỉ", key='number_of_per_pack', value='10')

        db.session.add_all([superadmin, medical_expenses, patients_per_day_config, number_of_per_pack])
        db.session.commit()
