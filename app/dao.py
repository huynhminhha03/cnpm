from app.models import BenhNhan,ChiTietBenhNhan,LichKham,Favor,CMND,BHYT,Address,UserRoleEnum
from app import app
import hashlib


def get_benhnhan_by_id(id):
    return BenhNhan.query.get(id)

def get_lichkham_by_ngaykham(ngaykham):
    lichkham = LichKham.query

    if ngaykham:
        lichkham = lichkham.filter_by(ngaykham=ngaykham).first()

    return lichkham