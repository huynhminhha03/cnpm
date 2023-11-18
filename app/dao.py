from app.models import BenhNhan, ChiTietBenhNhan, LichKham, DanhSachKhamBenh, Favor, CMND, BHYT, Address, UserRoleEnum
from app import app
import hashlib


def get_benhnhan_by_id(id):
    return BenhNhan.query.get(id)


def get_lichkham_by_ngaykham(ngaykham):
    lichkham = LichKham.query

    if ngaykham:
        lichkham = lichkham.filter_by(ngaykham=ngaykham).first()

    return lichkham


def count_danhsachkhambenh_theolichkham(id_lichkham):
    return DanhSachKhamBenh.query.filter_by(lichkham_id=id_lichkham).count()


def get_lichkham_by_id(id_lichkham):
    return LichKham.query.get(id_lichkham)


def get_duplicate_benhnhan_name_by_sdt(name , sdt):
    benhnhan = None

    benhnhan = BenhNhan.query.filter_by(sdt=sdt,ten_benhnhan = name).first()

    return benhnhan


def get_cmnd_by_soCMND(soCMND):
    cmnd = CMND.query
    if soCMND:
        cmnd = cmnd.filter_by(so_cmnd=soCMND).first()

    return cmnd


def get_bhyt_by_soBHYT(soBHYT):
    bhyt = BHYT.query

    if soBHYT:
        bhyt = bhyt.filter_by(so_bhyt=soBHYT).first()

    return bhyt


def get_chitietbenhnhan_by_address(chitietbn_id, newAddress):
    address = None
    address = Address.query.filter_by(chitiet_benhnhan_id=chitietbn_id , ten_diachi = newAddress).first()

    return address



def get_chitietbenhnhan_by_benhnhan_id(benhnhan_id):
    chitietbenhnhan = None

    if benhnhan_id:
        chitietbenhnhan = ChiTietBenhNhan.query.filter_by(benhnhan_id=benhnhan_id).first()

    return chitietbenhnhan