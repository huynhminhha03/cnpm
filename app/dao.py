from app.models import BenhNhan, ChiTietBenhNhan, LichKham, DanhSachKhamBenh, Favor, CMND, BHYT, Address, UserRoleEnum
from app import app
import hashlib


def get_benhnhan_by_id(id):
    return BenhNhan.query.get(id)

def get_chitietbenhnhan_by_benhnhan_id(benhnhan_id):
    chitietbenhnhan = None

    if benhnhan_id:
        chitietbenhnhan = ChiTietBenhNhan.query.filter_by(benhnhan_id=benhnhan_id).first()

    return chitietbenhnhan

def get_chitietbenhnhan_by_sdt(sdt):
    chitietbenhnhan = None

    if sdt:
        chitietbenhnhan = ChiTietBenhNhan.query.filter_by(sdt=sdt).first()

    return chitietbenhnhan

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

def get_lichkham_by_ngaykham(ngaykham):
    lichkham = LichKham.query

    if ngaykham:
        lichkham = lichkham.filter_by(ngaykham=ngaykham).first()

    return lichkham



def count_danhsachkhambenh_theo_lichkham(id_lichkham):
    return DanhSachKhamBenh.query.filter_by(lichkham_id=id_lichkham).count()



def get_lichkham_by_id(id_lichkham):
    return LichKham.query.get(id_lichkham)


def get_duplicate_dangkikhambenh_by_2id(id_bn , id_lk):
    dangkikhambenh= None

    dangkikhambenh = DanhSachKhamBenh.query.filter_by(benhnhan_id=id_bn,lichkham_id = id_lk).first()

    return dangkikhambenh






