from sqlalchemy.sql import extract

from app import db
from app.models import LoaiThuoc, DonViThuoc, PhieuKhamBenh, HoaDonThanhToan, LoaiThuoc_DonViThuoc, DsLieuLuongThuoc


def medicine_report(from_date, to_date):
    if not from_date > to_date:
        from_date += ' 00:00:00'
        to_date += ' 23:59:59'
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

        # ex/ Xử lý LoaiThuoc_DonViThuoc.id trung lap
        result_dict = {}

        for item in result:
            key = item[0]
            if key in result_dict:
                # ex/ Nếu key đã tồn tại, cập nhật các giá trị khác
                result_dict[key][3] += item[3]  # ex/ Cập nhật giá trị thứ tư (số lượng)
                result_dict[key][-1] += 1  # ex/ Cập nhật giá trị cuối cùng (số lần xuất hiện)
            else:
                # ex/ Nếu key chưa tồn tại, thêm mới vào result_dict
                result_dict[key] = list(item)
                result_dict[key][-1] = 1  # ex/ Số lần xuất hiện đầu tiên

        # ex/ Chuyển result_dict thành list
        result = list(result_dict.values())
        return result
    return []


def revenue_report(month):
    if month > '0000-00':
        # ex/ print(month)
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

        # ex/ Xử lý 1 bệnh nhân có nhiều hóa đơn trong ngày
        result_dict = {}

        for item in s:
            key = (item[0], item[1])  # ex/ Tạo khóa từ ngày và id
            if key in result_dict:
                # ex/ Nếu khóa đã tồn tại, cập nhật tổng cộng
                result_dict[key][2] += item[2]
            else:
                # ex/ Nếu khóa chưa tồn tại, thêm mới vào từ điển
                result_dict[key] = list(item)

        # ex/ Sử dụng list comprehension để chuyển từ điển thành danh sách chứa các tuple
        # ex/ result_list = [tuple(value) for value in result_dict.values()]
        result_list = list(result_dict.values())
        # ex/ Xử lý đếm bệnh nhân trong 1 ngày
        result_dict = {}

        for item in result_list:
            key = item[0]  # ex/ Sử dụng ngày làm key
            if key in result_dict:
                # ex/ Nếu khóa đã tồn tại, cập nhật bệnh nhân & tổng cộng
                result_dict[key] = (key, result_dict[key][1] + 1, result_dict[key][2] + item[2])
            else:
                # ex/ Nếu khóa chưa tồn tại, thêm mới vào từ điển & chỉnh id -> số bn trong ngày
                result_dict[key] = list(item)
                result_dict[key][1] = 1
        # ex/ Sử dụng list comprehension để chuyển từ điển thành danh sách chứa các tuple
        result_list = [tuple(value) for value in result_dict.values()]

        total_value = sum(item[2] for item in result_list)
        result_list_with_ratio = [(item[0], item[1], item[2], round((item[2] / total_value) * 100, 2)) for item in
                                  result_list]

        return result_list_with_ratio
    return []
