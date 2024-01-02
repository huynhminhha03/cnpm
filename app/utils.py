from sqlalchemy import func
from app import dao, db
from app.models import BenhNhan, ChiTietBenhNhan, DanhSachKhamBenh, Address, CMND, BHYT, UserRoleEnum, \
    Manager, Config, LoaiThuoc, DonViThuoc, PhieuKhamBenh, HoaDonThanhToan, LoaiThuoc_DonViThuoc, DsLieuLuongThuoc


def MedicineReport():
    l1 = db.session.query(LoaiThuoc_DonViThuoc.id, DsLieuLuongThuoc.soluong) \
        .join(LoaiThuoc_DonViThuoc, LoaiThuoc_DonViThuoc.id.__eq__(DsLieuLuongThuoc.loaithuoc_donvithuoc_id)) \
        .order_by(LoaiThuoc_DonViThuoc.id.asc()).all()
    # Custom số lượng
    dict_l1 = {}

    for item in l1:
        key = item[0]
        value = item[1]
        dict_l1[key] = dict_l1.get(key, 0) + value

    # Chuyển đổi dict thành danh sách tuples
    result_l1 = list(dict_l1.items())

    l2 = db.session.query(LoaiThuoc_DonViThuoc.id, LoaiThuoc.ten_loaithuoc, DonViThuoc.ten_donvithuoc,
                          func.count(DsLieuLuongThuoc.loaithuoc_donvithuoc_id)) \
        .join(DsLieuLuongThuoc, LoaiThuoc_DonViThuoc.id == DsLieuLuongThuoc.loaithuoc_donvithuoc_id) \
        .join(LoaiThuoc, LoaiThuoc_DonViThuoc.loaithuoc_id == LoaiThuoc.id) \
        .join(DonViThuoc, LoaiThuoc_DonViThuoc.donvithuoc_id == DonViThuoc.id) \
        .order_by(LoaiThuoc_DonViThuoc.id.asc()) \
        .group_by(LoaiThuoc_DonViThuoc.id) \
        .all()

    result_l2 = []
    if len(result_l1) == len(l2):
        dict_l2 = {item[0]: item[1:] for item in l2}

        for item_l1 in result_l1:
            key = item_l1[0]
            # Nếu key có trong từ điển l2, thực hiện cập nhật
            if key in dict_l2:
                result_l2.append(tuple(list(dict_l2[key]) + [item_l1[1]]))
                del dict_l2[key]  # Bỏ đi phần tử đã được sử dụng
    return result_l2
