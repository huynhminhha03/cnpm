from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose
from flask_admin.form.upload import ImageUploadField
from app import app, db, admin, dao
from flask_login import logout_user, current_user
from flask import redirect, request
from app.models import BenhNhan, ChiTietBenhNhan, LichKham, DanhSachKhamBenh, Favor, Address, CMND, BHYT, UserRoleEnum, \
    Manager
import os
from datetime import datetime
import cloudinary
from cloudinary.uploader import upload
from wtforms.validators import InputRequired
from wtforms import SelectField, PasswordField, validators

auto_increment_number = 0

cloudinary.config(
    cloud_name="diwxda8bi",
    api_key="358748635141677",
    api_secret="QBGsplvCUjvxqZFWkpQBWKFT91I"
)


class AuthenticatedUser(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class AuthenticatedYTa(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.Y_TA


class CustomManagerModelView(ModelView):
    form_create_rules = [
        'ten_quantri', 'username', 'password', 'gioitinh', 'cmnd', 'sdt', 'ngaysinh', 'hinhanh', 'diachi', 'user_role'
    ]

    column_labels = {'ten_quantri': 'Họ và tên', 'username': 'Tên người dùng', 'password': 'Mật khẩu',
                     'gioitinh': 'Giới tính','hinhanh': 'Hình ảnh',
                     'cmnd': 'Số chứng minh nhân dân', 'sdt': 'Số điện thoại',
                     'ngaysinh': 'Ngày sinh', 'diachi': 'Địa chỉ', 'user_role': 'Chức vụ'}  # Đổi tên trường

    form_extra_fields = {
        'hinhanh': ImageUploadField('Hình ảnh', base_path=app.config['UPLOAD_FOLDER'],
                                    thumbnail_size=(100, 100, True), validators=[InputRequired()]),
        'gioitinh': SelectField('Giới tính', choices=[('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Khác', 'Khác')],
                                validators=[InputRequired()]),
        'password': PasswordField('Mật khẩu', validators=[validators.DataRequired()])
    }

    def on_model_change(self, form, model, is_created):
        super().on_model_change(form, model, is_created)
        image_path = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], model.hinhanh)

        # Tải lên hình ảnh lên Cloudinary
        response = upload(image_path)
        model.hinhanh = response['secure_url']

        # Xóa hình ảnh cục bộ sau khi tải lên Cloudinary
        os.remove(image_path)

    def create_model(self, form):
        model = self.model()
        form.populate_obj(model)

        # Tùy chỉnh xử lý trước khi lưu vào cơ sở dữ liệu
        import hashlib
        manager = Manager(ten_quantri=model.ten_quantri
                          , username=model.username
                          , password=str(hashlib.md5(model.password.encode('utf-8')).hexdigest())
                          , gioitinh=model.gioitinh, cmnd=model.cmnd, sdt=model.sdt,
                          ngaysinh=datetime.strptime(str(model.ngaysinh), "%Y-%m-%d %H:%M:%S")
                          , hinhanh=model.hinhanh, diachi=model.diachi, user_role=model.user_role)

        self.session.add(manager)
        self._on_model_change(form, manager, True)

        self.session.commit()
        return True


class AuthenticatedAdmin(CustomManagerModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.ADMIN


class MyManagerView(AuthenticatedAdmin):
    column_list = ['id', 'username', 'ten_quantri', 'gioitinh', 'cmnd', 'sdt', 'ngaysinh', 'hinhanh', 'diachi',
                   'user_role']
    column_searchable_list = ['id', 'ten_quantri', 'gioitinh', 'cmnd', 'sdt', 'ngaysinh', 'hinhanh', 'diachi',
                              'user_role']
    can_create = True
    can_delete = True
    can_edit = True


class MyDanhSachKhamBenhView(AuthenticatedYTa):
    column_list = ['STT', 'dskb_lichkham', 'benhnhan_name', 'chitietbenhnhan_gioitinh',
                   'chitietbenhnhan_ngaysinh',
                   'chitietbenhnhan_diachi']
    column_labels = {'dskb_lichkham': 'Lịch khám', 'benhnhan_name': 'Họ tên', 'chitietbenhnhan_gioitinh': 'Giới tính'
        , 'chitietbenhnhan_ngaysinh': 'Năm sinh', 'chitietbenhnhan_diachi': 'Địa chỉ'}  # Đổi tên trường

    column_searchable_list = ['lichkham_id']

    def _stt_formatter(self, context, model, name):
        global auto_increment_number

        # Sử dụng số tự tăng và sau đó tăng giá trị cho lần nạp tiếp theo
        current_number = auto_increment_number

        auto_increment_number += 1
        sl = dao.count_danhsachkhambenh_theo_lichkham(model.lichkham_id)
        str_num = str(auto_increment_number)
        if auto_increment_number == sl:
            auto_increment_number = 0

        return str_num

    def _dskb_lichkham_formatter(self, context, model, name):
        lk = dao.get_lichkham_by_id(model.lichkham_id)
        return lk.ngaykham.strftime("%d/%m/%Y") if lk else 'Chưa cập nhật'

    def _benhnhan_ten_formatter(self, context, model, name):
        bn = dao.get_benhnhan_by_id(model.benhnhan_id)
        return bn.ten_benhnhan if bn else 'Chưa cập nhật'

    def _chitietbenhnhan_gioiTinh_formatter(self, context, model, name):
        ctbn = dao.get_chitietbenhnhan_by_benhnhan_id(model.benhnhan_id)
        return ctbn.gioitinh if ctbn else 'Chưa cập nhật'

    def _chitietbenhnhan_ngaysinh_formatter(self, context, model, name):
        ctbn = dao.get_chitietbenhnhan_by_benhnhan_id(model.benhnhan_id)
        return ctbn.ngaysinh.year if ctbn else 'Chưa cập nhật'

    def _chitietbenhnhan_diachi_formatter(self, context, model, name):
        ctbn = dao.get_chitietbenhnhan_by_benhnhan_id(model.benhnhan_id)
        diachi = dao.get_diachi_by_ctbn_id(ctbn.id)
        return diachi.ten_diachi if diachi else 'Chưa cập nhật'

    column_formatters = {
        'STT': _stt_formatter,
        'dskb_lichkham': _dskb_lichkham_formatter,
        'benhnhan_name': _benhnhan_ten_formatter,
        'chitietbenhnhan_gioitinh': _chitietbenhnhan_gioiTinh_formatter,
        'chitietbenhnhan_diachi': _chitietbenhnhan_diachi_formatter,
        'chitietbenhnhan_ngaysinh': _chitietbenhnhan_ngaysinh_formatter,
    }

    can_create = False
    can_export = True
    can_view_details = True


class MyLogoutView(AuthenticatedUser):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/admin')


if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

admin.add_view(MyDanhSachKhamBenhView(DanhSachKhamBenh, db.session))
admin.add_view(MyManagerView(Manager, db.session))
admin.add_view(MyLogoutView(name='Đăng xuất'))
