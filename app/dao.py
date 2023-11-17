from app.models import BenhNhan,ChiTietBenhNhan,Favor,CMND,BHYT,Address,UserRoleEnum
from app import app
import hashlib


def get_benhnhan_by_id(id):
    return BenhNhan.query.get(id)
