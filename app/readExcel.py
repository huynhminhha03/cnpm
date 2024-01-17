import pandas as pd

excel_file_path = "C:/Users/Lenovo/Desktop/BTL CNPM/cnpm/Danh_Sach_Kham_Benh_2024-01-08_16-43-07.xlsx"
# Đọc file Excel với chỉ định trang
sheet_name = 'Danh_Sach_Kham_Benh_2024-01 (2)'
# Tên cột cần đọc
column_name = 'Số điện thoại'

df = pd.read_excel(excel_file_path, sheet_name=sheet_name, usecols=[column_name])

# Lấy dữ liệu từ cột 'Số điện thoại'
phone = df[column_name].astype(str).tolist()

# Kiểm tra và thêm '0' vào đầu số điện thoại nếu cần thiết
phone = ['0' + number if not number.startswith('0') else number for number in phone]

# Hiển thị dữ liệu
for p in phone:
    print(p)
