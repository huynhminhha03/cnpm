
from app import dao, db
from app.models import BenhNhan, ChiTietBenhNhan, DanhSachKhamBenh, Address, CMND, BHYT, UserRoleEnum, \
    Manager, Config, LoaiThuoc, DonViThuoc, PhieuKhamBenh, HoaDonThanhToan, LoaiThuoc_DonViThuoc, DsLieuLuongThuoc
from sqlalchemy.sql import extract


def medicine_report(from_date, to_date):
    if not from_date > to_date:
        from_date += ' 00:00:00'
        to_date += ' 23:59:59'
        # print(from_date)
        # print(to_date)
        result = db.session.query(
            LoaiThuoc_DonViThuoc.id,
            LoaiThuoc.ten_loaithuoc,
            DonViThuoc.ten_donvithuoc,
            DsLieuLuongThuoc.soluong,
            PhieuKhamBenh.ngaylapphieukham
        ).join(DsLieuLuongThuoc, LoaiThuoc_DonViThuoc.id == DsLieuLuongThuoc.loaithuoc_donvithuoc_id
               ).join(PhieuKhamBenh, PhieuKhamBenh.id == DsLieuLuongThuoc.phieukhambenh_id
                      ).join(LoaiThuoc, LoaiThuoc_DonViThuoc.loaithuoc_id == LoaiThuoc.id
                             ).join(DonViThuoc, LoaiThuoc_DonViThuoc.donvithuoc_id == DonViThuoc.id
                                    ).filter(
                                        PhieuKhamBenh.ngaylapphieukham.between(from_date, to_date)
        ).all()

        # Xử lý LoaiThuoc_DonViThuoc.id trung lap
        result_dict = {}

        for item in result:
            key = item[0]
            if key in result_dict:
                # Nếu key đã tồn tại, cập nhật các giá trị khác
                result_dict[key][3] += item[3]  # Cập nhật giá trị thứ tư (số lượng)
                result_dict[key][-1] += 1  # Cập nhật giá trị cuối cùng (số lần xuất hiện)
            else:
                # Nếu key chưa tồn tại, thêm mới vào result_dict
                result_dict[key] = list(item)
                result_dict[key][-1] = 1  # Số lần xuất hiện đầu tiên

        # Chuyển result_dict thành list
        result = list(result_dict.values())
        return result
    return []


def revenue_report(month):
    if month > '0000-00':
        # print(month)
        s = db.session.query(
            HoaDonThanhToan.ngaythanhtoanhoadon,
            HoaDonThanhToan.benhnhan_id,
            HoaDonThanhToan.tongcong
        ).filter(
            extract('month', HoaDonThanhToan.ngaythanhtoanhoadon) == int(month.split('-')[1]),
            extract('year', HoaDonThanhToan.ngaythanhtoanhoadon) == int(month.split('-')[0]),
            HoaDonThanhToan.trangthai == 1
        ).order_by(
            HoaDonThanhToan.ngaythanhtoanhoadon.asc()
        ).all()

        # Xử lý 1 bệnh nhân có nhiều hóa đơn trong ngày
        result_dict = {}

        for item in s:
            key = (item[0], item[1])  # Tạo khóa từ ngày và id
            if key in result_dict:
                # Nếu khóa đã tồn tại, cập nhật tổng cộng
                result_dict[key][2] += item[2]
            else:
                # Nếu khóa chưa tồn tại, thêm mới vào từ điển
                result_dict[key] = list(item)

        # Sử dụng list comprehension để chuyển từ điển thành danh sách chứa các tuple
        # result_list = [tuple(value) for value in result_dict.values()]
        result_list = list(result_dict.values())
        # Xử lý đếm bệnh nhân trong 1 ngày
        result_dict = {}

        for item in result_list:
            key = item[0]  # Sử dụng ngày làm key
            if key in result_dict:
                # Nếu khóa đã tồn tại, cập nhật bệnh nhân & tổng cộng
                result_dict[key] = (key, result_dict[key][1] + 1, result_dict[key][2] + item[2])
            else:
                # Nếu khóa chưa tồn tại, thêm mới vào từ điển & chỉnh id -> số bn trong ngày
                result_dict[key] = list(item)
                result_dict[key][1] = 1
        # Sử dụng list comprehension để chuyển từ điển thành danh sách chứa các tuple
        result_list = [tuple(value) for value in result_dict.values()]

        total_value = sum(item[2] for item in result_list)
        result_list_with_ratio = [(item[0], item[1], item[2], round((item[2] / total_value) * 100, 2)) for item in result_list]

        return result_list_with_ratio
    return []
    # for item in result_list:
    #
    # ele = len(result_list)
    # return ele
    # return db.session.query(
    #     HoaDonThanhToan.ngaythanhtoanhoadon,
    #     func.count(HoaDonThanhToan.benhnhan_id),
    #     func.sum(HoaDonThanhToan.tongcong)
    # ).filter(
    #         HoaDonThanhToan.trangthai == 1,
    # ).group_by(HoaDonThanhToan.ngaythanhtoanhoadon).all()


# print(revenue_report())