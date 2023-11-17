from app.models import BenhNhan,ChiTietBenhNhan,Email,CMND,BHYT
from app import app
import hashlib


def get_benhnhan_by_id(id):
    return BenhNhan.query.get(id)
