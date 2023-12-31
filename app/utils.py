from sqlalchemy import func
from app import db
from app.models import BenhNhan, ChiTietBenhNhan, DanhSachKhamBenh, Address, CMND, BHYT, UserRoleEnum, \
    Manager, Config, LoaiThuoc, DonViThuoc, PhieuKhamBenh, HoaDonThanhToan, LoaiThuoc_DonViThuoc, DsLieuLuongThuoc


def MedicineReport():
    return db.session.query(LoaiThuoc.id, LoaiThuoc.ten_loaithuoc, func.count(DsLieuLuongThuoc.id))\
        .join(LoaiThuoc_DonViThuoc, LoaiThuoc_DonViThuoc.loaithuoc_id.__eq__(LoaiThuoc.id))\
        .join(DsLieuLuongThuoc, DsLieuLuongThuoc.loaithuoc_donvithuoc_id.__eq__(LoaiThuoc_DonViThuoc.id), isouter=True)\
        .group_by(LoaiThuoc.id, LoaiThuoc.ten_loaithuoc).order_by(LoaiThuoc.id.asc()).all()

    # Cach2
    # return db.session.query(LoaiThuoc.id, LoaiThuoc.ten_loaithuoc, func.count(DsLieuLuongThuoc.id)) \
    #     .join(LoaiThuoc_DonViThuoc, LoaiThuoc_DonViThuoc.loaithuoc_id == LoaiThuoc.id) \
    #     .outerjoin(DsLieuLuongThuoc, DsLieuLuongThuoc.loaithuoc_donvithuoc_id == LoaiThuoc_DonViThuoc.id) \
    #     .group_by(LoaiThuoc.id, LoaiThuoc.ten_loaithuoc).order_by(LoaiThuoc.id.asc()).all()


# print(MedicineReport())
# Tra ve ds LoaiThuoc_DonViThuoc chua cac phan tu thuoc DSLieuLuongThuoc
# Dung 'isouter=True' Tra ve ds LoaiThuoc_DonViThuoc chua cac phan tu thuoc&kothuoc DSLieuLuongThuoc