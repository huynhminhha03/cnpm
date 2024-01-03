from flask_admin.contrib.sqla import ModelView
import hashlib
import hmac
import json
import os
import requests
import uuid
from datetime import datetime

import cloudinary
from cloudinary.uploader import upload
from flask import redirect, flash, url_for, render_template, request
from flask_admin import BaseView, expose, Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.upload import ImageUploadField
from flask_login import logout_user, current_user
from markupsafe import Markup
from wtforms import SelectField, PasswordField, validators, DateField, StringField
from wtforms.validators import InputRequired

from app import app, db, dao, utils
from app.models import BenhNhan, ChiTietBenhNhan, DanhSachKhamBenh, Address, CMND, BHYT, UserRoleEnum, \
    Manager, Config, LoaiThuoc, PhieuKhamBenh, HoaDonThanhToan

cloudinary.config(
    cloud_name="diwxda8bi",
    api_key="358748635141677",
    api_secret="QBGsplvCUjvxqZFWkpQBWKFT91I"
)


class AuthenticatedUser(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class MyLogoutView(AuthenticatedUser):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/admin')


if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


def delete_images_in_folder(folder_path):
    # Kiểm tra xem thư mục tồn tại hay không
    if not os.path.exists(folder_path):
        print(f"Thư mục {folder_path} không tồn tại.")
        return

    # Duyệt qua tất cả các tệp trong thư mục
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        # Kiểm tra xem tệp có phải là 'png' hoặc 'jpg' không
        if file_name.lower().endswith(('.png', '.jpg')):
            try:
                # Xóa tệp nếu có đuôi là 'png' hoặc 'jpg'
                os.remove(file_path)
                print(f"Đã xóa tệp {file_name}")
            except Exception as e:
                print(f"Lỗi khi xóa tệp {file_name}: {e}")


class CustomAdminManagerModelView(ModelView):
    form_create_rules = [
        'ten_quantri', 'username', 'password', 'gioitinh', 'cmnd', 'sdt', 'ngaysinh', 'hinhanh', 'diachi', 'user_role'
    ]

    form_edit_rules = [
        'ten_quantri', 'username', 'gioitinh', 'cmnd', 'sdt', 'ngaysinh', 'hinhanh', 'diachi', 'user_role'
    ]

    column_labels = {'ten_quantri': 'Họ và tên', 'username': 'Tên người dùng', 'password': 'Mật khẩu',
                     'gioitinh': 'Giới tính', 'hinhanh': 'Hình ảnh',
                     'cmnd': 'Số chứng minh nhân dân', 'sdt': 'Số điện thoại',
                     'ngaysinh': 'Ngày sinh', 'diachi': 'Địa chỉ', 'user_role': 'Chức vụ'}  # Đổi tên trường

    form_extra_fields = {
        'username': StringField('Tên người dùng', [validators.DataRequired(),
                                                   validators.Regexp(r'^[a-zA-Z0-9_-]{3,20}$',
                                                                     message='Chỉ chứa ký tự chữ cái (thường và in '
                                                                             'hoa), số, gạch dưới, dấu gạch ngang và '
                                                                             'độ dài từ 3 đến 20 ký tự.')]),

        'ten_quantri': StringField('Họ và tên', [validators.DataRequired(),
                                                 validators.Regexp(
                                                     r'^[^\d!@#$%^&*()_+={}\[\]:;<>,.?~\\/-]+\s+[^\d!@#$%^&*()_+={}\['
                                                     r'\]:;<>,.?~\\/-]+(\s+[^\d!@#$%^&*()_+={}\[\]:;<>,.?~\\/-]+)?$',
                                                     message='Ex: David de Gea, Nguyễn Văn A, ...')]),

        'sdt': StringField('Số điện thoại', [validators.DataRequired(),
                                             validators.Regexp(r'^\d+$', message='Phải là những kí tự số !')]),

        'ngaysinh': DateField('Ngày sinh', validators=[InputRequired()], format="%Y-%m-%d"),

        'gioitinh': SelectField('Giới tính', choices=[('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Khác', 'Khác')],
                                validators=[InputRequired()]),

        'hinhanh': ImageUploadField('Hình ảnh', base_path=app.config['UPLOAD_FOLDER']),

        'diachi': StringField('Địa chỉ', validators=[InputRequired()]),

        'cmnd': StringField('Số chứng minh nhân dân', [validators.DataRequired(),
                                                       validators.Regexp(r'^\d+$',
                                                                         message='Phải là những kí tự số !')]),
        'user_role': SelectField('Chức vụ',
                                 choices=[('ADMIN', 'ADMIN'), ('BAC_SI', 'BAC_SI'), ('Y_TA', 'Y_TA')
                                     , ('THU_NGAN', 'THU_NGAN')],
                                 validators=[InputRequired()]),

        'password': PasswordField('Mật khẩu : ', validators=[InputRequired()]),

    }

    def create_model(self, form):
        username_existed = self.session.query(Manager).filter(Manager.username == form.username.data).first()
        cmnd_existed = self.session.query(Manager).filter(Manager.cmnd == form.cmnd.data).first()
        sdt_existed = self.session.query(Manager).filter(Manager.sdt == form.sdt.data).first()

        if not (username_existed or cmnd_existed or sdt_existed):
            model = self.model()
            form.populate_obj(model)
            # Tùy chỉnh xử lý trước khi lưu vào cơ sở dữ liệu
            if not model.hinhanh:
                hinhanh = ('https://res.cloudinary.com/diwxda8bi/image/upload/v1703312060/Adorable-animal-cat'
                           '-20787_ebmgss.jpg')
            else:
                hinhanh = model.hinhanh

            import hashlib
            manager = Manager(ten_quantri=model.ten_quantri
                              , username=model.username
                              , password=str(hashlib.md5(model.password.encode('utf-8')).hexdigest())
                              , gioitinh=model.gioitinh, cmnd=model.cmnd, sdt=model.sdt,
                              ngaysinh=datetime.strptime(str(model.ngaysinh), "%Y-%m-%d")
                              , hinhanh=hinhanh, diachi=model.diachi, user_role=model.user_role)

            self.session.add(manager)
            self._on_model_change(form, manager, True)
            self.session.commit()
            return True

        if username_existed:
            flash('Tên người dùng đã tồn tại', category='error')
        if cmnd_existed:
            flash('Số CMND đã tồn tại', category='error')
        if sdt_existed:
            flash('Số điện thoại đã tồn tại', category='error')
        self.session.rollback()
        return False

    def on_form_prefill(self, form, id):
        manager = dao.get_manager_by_id(id)

    def on_model_change(self, form, model, is_created):
        super().on_model_change(form, model, is_created)
        image_path = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], model.hinhanh)
        # Hiển thị đường dẫn của hình đã lưu vào thư mục cục bộ
        print(image_path)

        # Kiểm tra xem có hình ảnh mới được tải lên hay không
        if form.hinhanh.data:
            # Tải hình ảnh lên Cloudinary
            response = upload(image_path)
            model.hinhanh = response['secure_url']

            # Xóa hình ảnh cục bộ sau khi tải lên Cloudinary
            delete_images_in_folder(app.config['UPLOAD_FOLDER'])
        else:
            # Nếu không có hình mới, giữ nguyên URL hiện tại của model
            model.hinhanh = form.hinhanh.object_data['secure_url'] if form.hinhanh.object_data else None

    def update_model(self, form, model):

        manager = dao.get_manager_by_id(model.id)

        username_existed = self.session.query(Manager).filter(Manager.username == form.username.data).first()
        cmnd_existed = self.session.query(Manager).filter(Manager.cmnd == form.cmnd.data).first()
        sdt_existed = self.session.query(Manager).filter(Manager.sdt == form.sdt.data).first()

        if username_existed and manager.username != form.username.data:
            flash('Tên người dùng đã tồn tại', category='error')
            self.session.rollback()
            return False
        if cmnd_existed and manager.cmnd != form.cmnd.data:
            flash('Số CMND đã tồn tại', category='error')
            self.session.rollback()
            return False
        if sdt_existed and manager.sdt != form.sdt.data:
            flash('Số điện thoại đã tồn tại', category='error')
            self.session.rollback()
            return False

        # Tùy chỉnh xử lý trước khi lưu vào cơ sở dữ liệu
        manager.ten_quantri = form.ten_quantri.data
        manager.username = form.username.data
        manager.gioitinh = form.gioitinh.data
        manager.cmnd = form.cmnd.data
        manager.sdt = form.sdt.data
        manager.ngaysinh = form.ngaysinh.data
        manager.diachi = form.diachi.data
        manager.user_role = form.user_role.data

        file_storage = form.hinhanh.data
        # Lấy tên của tệp tin
        filename = file_storage.filename
        manager.hinhanh = filename

        self.session.add(manager)
        self._on_model_change(form, manager, True)  # error chua fix
        self.session.commit()
        return True


class AuthenticatedAdminManager(CustomAdminManagerModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.ADMIN


class MyManagerView(AuthenticatedAdminManager):
    column_list = ['id', 'username', 'ten_quantri', 'gioitinh', 'cmnd', 'sdt', 'ngaysinh', 'hinhanh', 'diachi',
                   'user_role']
    column_searchable_list = ['id', 'ten_quantri', 'gioitinh', 'cmnd', 'sdt', 'ngaysinh', 'hinhanh', 'diachi',
                              'user_role']
    can_create = True
    can_delete = False
    can_edit = True


class AuthenticatedAdminConfig(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.ADMIN


class MyConfigView(AuthenticatedAdminConfig):
    column_list = ['id', 'ten_config', 'value']
    column_searchable_list = ['ten_config', 'value']
    can_edit = True
    can_create = True
    can_delete = False


class CustomYTaDSKBModelView(ModelView):
    column_list = ['stt', 'dskb_lichkham', 'benhnhan_name', 'chitietbenhnhan_gioitinh',
                   'chitietbenhnhan_ngaysinh',
                   'chitietbenhnhan_diachi']
    column_labels = {'stt': 'Số thứ tự', 'dskb_lichkham': 'Lịch khám', 'benhnhan_name': 'Họ tên',
                     'chitietbenhnhan_gioitinh': 'Giới tính'
        , 'chitietbenhnhan_ngaysinh': 'Năm sinh', 'chitietbenhnhan_diachi': 'Địa chỉ'}  # Đổi tên trường

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
        'dskb_lichkham': _dskb_lichkham_formatter,
        'benhnhan_name': _benhnhan_ten_formatter,
        'chitietbenhnhan_gioitinh': _chitietbenhnhan_gioiTinh_formatter,
        'chitietbenhnhan_diachi': _chitietbenhnhan_diachi_formatter,
        'chitietbenhnhan_ngaysinh': _chitietbenhnhan_ngaysinh_formatter,
    }

    column_searchable_list = ('lichkham.ngaykham',)
    column_filters = ['lichkham.ngaykham']

    # 2 hàm ghi đè này chưa đè đc ?
    def _search_placeholder(self):
        return "Tim kiếm ngày theo định dạng năm-tháng-ngày"

    def search(self, query, search_term):
        # Ghi đè hàm search để tùy chỉnh quá trình tìm kiếm
        search_term = datetime.strptime(search_term, "%Y-%m-%d")
        lichkham = dao.get_lichkham_by_ngaykham(search_term)
        return DanhSachKhamBenh.query.filter_by(lichkham_id=lichkham.id).all()


class AuthenticatedYTaDSKB(CustomYTaDSKBModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.Y_TA


class MyDanhSachKhamBenhView(AuthenticatedYTaDSKB):
    can_export = True
    can_edit = False


class CustomYTaBenhNhanModelView(ModelView):
    # custom show information detail

    column_list = ['id', 'ten_benhnhan', 'chitietbenhnhan.gioitinh', 'chitietbenhnhan.sdt',
                   'chitietbenhnhan.ngaysinh',
                   'chitietbenhnhan.diachi', 'chitietbenhnhan.cmnd', 'chitietbenhnhan.bhyt']

    column_labels = {'id': 'Mã bệnh nhân', 'ten_benhnhan': 'Họ tên bệnh nhân', 'benhnhan_name': 'Họ tên',
                     'chitietbenhnhan.gioitinh': 'Giới tính', 'chitietbenhnhan.sdt': 'Số điện thoại'
        , 'chitietbenhnhan.ngaysinh': 'Năm sinh', 'chitietbenhnhan.diachi': 'Địa chỉ',
                     'chitietbenhnhan.bhyt': 'Số bảo hiểm y tế',
                     'chitietbenhnhan.cmnd': 'Số chứng minh nhân dân'}  # Đổi tên trường

    column_searchable_list = ('chitietbenhnhan.sdt',)
    column_filters = ['chitietbenhnhan.sdt']

    def _benhnhan_gioitinh_formatter(self, context, model, name):
        ctbn = dao.get_chitietbenhnhan_by_benhnhan_id(model.id)
        return ctbn.gioitinh if ctbn else 'Chưa cập nhật'

    def _benhnhan_sdt_formatter(self, context, model, name):
        ctbn = dao.get_chitietbenhnhan_by_benhnhan_id(model.id)
        return ctbn.sdt if ctbn else 'Chưa cập nhật'

    def _benhnhan_ngaysinh_formatter(self, context, model, name):
        ctbn = dao.get_chitietbenhnhan_by_benhnhan_id(model.id)
        return ctbn.ngaysinh.year if ctbn else 'Chưa cập nhật'

    def _benhnhan_diachi_formatter(self, context, model, name):
        ctbn = dao.get_chitietbenhnhan_by_benhnhan_id(model.id)
        diachi = dao.get_diachi_by_ctbn_id(ctbn.id)
        if diachi:
            return diachi.ten_diachi
        else:
            return 'Chưa cập nhật'

    def _benhnhan_cmnd_formatter(self, context, model, name):
        ctbn = dao.get_chitietbenhnhan_by_benhnhan_id(model.id)
        cmnd = dao.get_cmnd_by_ctbn_id(ctbn.id)
        if cmnd:
            return cmnd.so_cmnd
        else:
            return 'Chưa cập nhật'

    def _benhnhan_bhyt_formatter(self, context, model, name):
        ctbn = dao.get_chitietbenhnhan_by_benhnhan_id(model.id)
        bhyt = dao.get_bhyt_by_ctbn_id(ctbn.id)
        if bhyt:
            return bhyt.so_bhyt
        else:
            return 'Chưa cập nhật'

    column_formatters = {
        'chitietbenhnhan.gioitinh': _benhnhan_gioitinh_formatter,
        'chitietbenhnhan.sdt': _benhnhan_sdt_formatter,
        'chitietbenhnhan.ngaysinh': _benhnhan_ngaysinh_formatter,
        'chitietbenhnhan.diachi': _benhnhan_diachi_formatter,
        'chitietbenhnhan.cmnd': _benhnhan_cmnd_formatter,
        'chitietbenhnhan.bhyt': _benhnhan_bhyt_formatter,

    }

    # custom create Benh Nhan

    form_create_rules = [
        'ten_benhnhan', 'chitietbenhnhan.gioitinh', 'chitietbenhnhan.sdt', 'chitietbenhnhan.ngaysinh',
        'chitietbenhnhan.diachi',
        'chitietbenhnhan.cmnd',
        'chitietbenhnhan.bhyt',
    ]

    form_extra_fields = {
        'chitietbenhnhan.gioitinh': SelectField('Giới tính', choices=[('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Khác', 'Khác')],
                                                validators=[InputRequired()]),
        'chitietbenhnhan.sdt': StringField('Số điện thoại', [validators.DataRequired(),
                                                             validators.Regexp(r'^\d+$',
                                                                               message='Phải là những kí tự số !')]),
        'chitietbenhnhan.ngaysinh': DateField('Ngày sinh', validators=[InputRequired()]),
        'chitietbenhnhan.diachi': StringField('Địa chỉ'),
        'chitietbenhnhan.cmnd': StringField('Số chứng minh nhân dân'),
        'chitietbenhnhan.bhyt': StringField('Số bảo hiểm y tế'),

    }

    def create_model(self, form):

        model = self.model()
        form.populate_obj(model)
        sdt = getattr(model, 'chitietbenhnhan.sdt')
        so_cmnd = getattr(model, 'chitietbenhnhan.cmnd')
        so_bhyt = getattr(model, 'chitietbenhnhan.bhyt')

        existing_sdt = dao.get_chitietbenhnhan_by_sdt(sdt)
        existing_cmnd = dao.get_cmnd_by_soCMND(so_cmnd)
        existing_bhyt = dao.get_bhyt_by_soBHYT(so_bhyt)

        if existing_sdt:
            db.session.rollback()
            form['chitietbenhnhan.sdt'].errors.append('Số điện thoại này đã được đăng kí !')
            return False

        # Tùy chỉnh xử lý trước khi lưu vào cơ sở dữ liệu
        bn = BenhNhan(ten_benhnhan=model.ten_benhnhan, user_role=UserRoleEnum.BENH_NHAN)

        self.session.add(bn)
        self._on_model_change(form, bn, True)
        self.session.commit()

        ctbn = ChiTietBenhNhan(gioitinh=getattr(model, 'chitietbenhnhan.gioitinh'),
                               sdt=getattr(model, 'chitietbenhnhan.sdt'),
                               ngaysinh=getattr(model, 'chitietbenhnhan.ngaysinh'),
                               benhnhan_id=bn.id)
        self.session.add(ctbn)
        self._on_model_change(form, ctbn, True)
        self.session.commit()

        ten_diachi = getattr(model, 'chitietbenhnhan.diachi')
        if ten_diachi:
            diachi = Address(ten_diachi=ten_diachi, chitiet_benhnhan_id=ctbn.id)
            self.session.add(diachi)
            self._on_model_change(form, diachi, True)
            self.session.commit()

        if so_cmnd:
            if existing_cmnd:
                db.session.rollback()
                form['chitietbenhnhan.cmnd'].errors.append('Số CMND này đã được đăng kí !')
                return False
            cmnd = CMND(so_cmnd=so_cmnd, chitiet_benhnhan_id=ctbn.id)
            self.session.add(cmnd)
            self._on_model_change(form, cmnd, True)
            self.session.commit()

        if so_bhyt:
            if existing_bhyt:
                db.session.rollback()
                form['chitietbenhnhan.bhyt'].errors.append('Số BHYT này đã được đăng kí !')
                return False
            bhyt = BHYT(so_bhyt=so_bhyt, chitiet_benhnhan_id=ctbn.id)
            self.session.add(bhyt)
            self._on_model_change(form, bhyt, True)
            self.session.commit()

        return True

    # custom edit BenhNhan

    form_edit_rules = [
        'ten_benhnhan', 'chitietbenhnhan', 'benhnhanBackrefDanhSachKhamBenhs', 'chitietbenhnhan.gioitinh',
        'chitietbenhnhan.sdt',
        'chitietbenhnhan.ngaysinh',
        'chitietbenhnhan.diachi',
        'chitietbenhnhan.cmnd',
        'chitietbenhnhan.bhyt',
    ]

    # hidden foreign key input
    def on_form_prefill(self, form, id):
        # Lấy mô hình từ cơ sở dữ liệu
        model = self.get_one(id)

        if model:
            # Ẩn trường 'chitietbenhnhan' va truong backref trong biểu mẫu chỉnh sửa
            form.chitietbenhnhan.render_kw = {'style': 'display:none;'}
            form.chitietbenhnhan.label.text = ''  # Ẩn nhãn
            form.benhnhanBackrefDanhSachKhamBenhs.render_kw = {'style': 'display:none;'}
            form.benhnhanBackrefDanhSachKhamBenhs.label.text = ''  # Ẩn nhãn
            # Tự điền dữ liệu đã có sẵn :
            bn = dao.get_benhnhan_by_id(id)
            ctbn = dao.get_chitietbenhnhan_by_benhnhan_id(bn.id)
            form['chitietbenhnhan.sdt'].data = ctbn.sdt
            form['chitietbenhnhan.ngaysinh'].data = ctbn.ngaysinh
            diachi = dao.get_diachi_by_ctbn_id(ctbn.id)
            if diachi:
                form['chitietbenhnhan.diachi'].data = diachi.ten_diachi
            cmnd = dao.get_cmnd_by_ctbn_id(ctbn.id)
            if cmnd:
                form['chitietbenhnhan.cmnd'].data = cmnd.so_cmnd
            bhyt = dao.get_bhyt_by_ctbn_id(ctbn.id)
            if bhyt:
                form['chitietbenhnhan.bhyt'].data = bhyt.so_bhyt

    # custom edit
    def update_model(self, form, model):

        bn = dao.get_benhnhan_by_id(model.id)
        if bn:
            ctbn = dao.get_chitietbenhnhan_by_benhnhan_id(bn.id)

        sdt = form['chitietbenhnhan.sdt'].data
        so_cmnd = form['chitietbenhnhan.cmnd'].data
        so_bhyt = form['chitietbenhnhan.bhyt'].data
        ten_diachi = form['chitietbenhnhan.diachi'].data
        existing_cmnd = None
        existing_bhyt = None

        existing_sdt = dao.get_chitietbenhnhan_by_sdt(sdt)
        if so_cmnd:
            existing_cmnd = dao.get_cmnd_by_soCMND(so_cmnd)
        if so_bhyt:
            existing_bhyt = dao.get_bhyt_by_soBHYT(so_bhyt)

        if existing_sdt and ctbn.sdt != sdt:
            db.session.rollback()
            form['chitietbenhnhan.sdt'].errors.append('Số điện thoại này đã được đăng kí !')
            return False

        if existing_cmnd and existing_cmnd.so_cmnd != dao.get_cmnd_by_ctbn_id(ctbn.id).so_cmnd:
            db.session.rollback()
            form['chitietbenhnhan.cmnd'].errors.append('Số CMND này đã được đăng kí !')
            return False

        if existing_bhyt and existing_bhyt.so_bhyt != dao.get_bhyt_by_ctbn_id(ctbn.id).so_bhyt:
            db.session.rollback()
            form['chitietbenhnhan.bhyt'].errors.append('Số BHYT này đã được đăng kí !')
            return False

        # Thực hiện xử lý sau khi mô hình được thay đổi
        bn.ten_benhnhan = form['ten_benhnhan'].data
        ctbn.ngaysinh = form['chitietbenhnhan.ngaysinh'].data
        ctbn.gioitinh = form['chitietbenhnhan.gioitinh'].data
        ctbn.sdt = form['chitietbenhnhan.sdt'].data

        diachi = dao.get_diachi_by_ctbn_id(ctbn.id)
        if diachi and diachi.ten_diachi != ten_diachi:
            diachi.ten_diachi = form['chitietbenhnhan.diachi'].data
        elif not diachi and form['chitietbenhnhan.diachi'].data != '':
            diachi = Address(ten_diachi=form['chitietbenhnhan.diachi'].data, chitiet_benhnhan_id=ctbn.id)
            self.session.add(diachi)
            self.session.commit()

        cmnd = dao.get_cmnd_by_ctbn_id(ctbn.id)
        if cmnd and cmnd.so_cmnd != so_cmnd:
            cmnd.so_cmnd = form['chitietbenhnhan.cmnd'].data
        elif not cmnd and form['chitietbenhnhan.cmnd'].data != '':
            cmnd = CMND(so_cmnd=form['chitietbenhnhan.cmnd'].data, chitiet_benhnhan_id=ctbn.id)
            self.session.add(cmnd)
            self.session.commit()

        bhyt = dao.get_bhyt_by_ctbn_id(ctbn.id)
        if bhyt and bhyt.so_bhyt != so_bhyt:
            bhyt.so_bhyt = form['chitietbenhnhan.bhyt'].data
        elif not bhyt and form['chitietbenhnhan.bhyt'].data != '':
            bhyt = BHYT(so_bhyt=form['chitietbenhnhan.bhyt'].data, chitiet_benhnhan_id=ctbn.id)
            self.session.add(bhyt)
            self.session.commit()

        self.session.add(bn)
        self.session.add(ctbn)
        self.session.commit()

        return True


class AuthenticatedYTaBenhNhan(CustomYTaBenhNhanModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.Y_TA


class MyBenhNhanView(AuthenticatedYTaBenhNhan):
    can_create = True
    can_export = True
    can_view_details = True
    can_delete = False


class CustomYTaDKKBModelView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/medical_examination.html')


class AuthenticatedYTaDKKB(CustomYTaDKKBModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.Y_TA


class MyDKKBView(AuthenticatedYTaDKKB):
    pass


class CustomBacSiLoaiThuocView(ModelView):
    column_list = ['ten_loaithuoc']

    column_labels = {'ten_loaithuoc': 'Tên loại thuốc'}  # Đổi tên trường

    column_searchable_list = ('ten_loaithuoc',)


class AuthenticatedBacSiLoaiThuoc(CustomBacSiLoaiThuocView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.BAC_SI


class MyThuocView(AuthenticatedBacSiLoaiThuoc):
    can_create = False
    can_delete = False
    can_edit = False


class CustomBacSiLPKModelView(BaseView):
    @expose('/')
    def indexBacSiLPK(self):
        today = datetime.now().strftime('%Y-%m-%d')
        loaithuoc = dao.load_loaithuoc()
        donvithuoc = dao.load_donvithuoc()
        return self.render('admin/medical_report.html', today=today, loaithuoc=loaithuoc, donvithuoc=donvithuoc)


class AuthenticatedBacSiLPK(CustomBacSiLPKModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.BAC_SI


class MyLPKView(AuthenticatedBacSiLPK):
    pass


class CustomBacSiTraCuuLSBenhNhanView(ModelView):
    column_list = ['ten_nguoidangki', 'ten_nguoikham', 'lichkham.ngaykham', 'trieuchung', 'dudoanbenh'
        , 'dslieuluongthuoc']

    column_labels = {'id': 'Mã phiếu khám', 'ten_nguoidangki': 'Tên người đăng kí', 'ten_nguoikham': 'Tên người khám',
                     'sdt': 'Số điện thoại'
        , 'lichkham.ngaykham': 'Ngày khám', 'trieuchung': 'Triệu chứng', 'dudoanbenh': 'Dự đoán bệnh',
                     'dslieuluongthuoc': 'Danh sách thuốc'}  # Đổi tên trường

    column_searchable_list = ('ten_nguoikham', 'sdt')
    column_filters = ['lichkham.ngaykham']

    def _traCuuLSBenhNhan_benhnhan_formatter(self, context, model, name):
        bn = dao.get_benhnhan_by_id(model.benhnhan_id)
        return bn.ten_benhnhan if bn else 'Chưa cập nhật'

    def _traCuuLSBenhNhan_lichkham_formatter(self, context, model, name):
        return model.lichkham.ngaykham.strftime("%d/%m/%Y") if model.lichkham else 'Chưa cập nhật'

    def _traCuuLSBenhNhan_dslieuluongthuoc_formatter(self, context, model, name):
        results = []
        dsllt = dao.get_dsLieuLuongThuoc_by_phieuKhamBenh_id(model.id)

        for d in dsllt:
            loaithuoc_donvithuoc = dao.get_loaithuoc_donvithuoc_by_id(d.loaithuoc_donvithuoc_id)
            loaithuoc = dao.get_loaithuoc_by_id(loaithuoc_donvithuoc.loaithuoc_id)
            donvithuoc = dao.get_donvithuoc_by_id(loaithuoc_donvithuoc.donvithuoc_id)
            soluong = str(d.soluong)
            motLoaiThuoc = loaithuoc.ten_loaithuoc + '(' + soluong + '/' + donvithuoc.ten_donvithuoc + ')'
            results.append(motLoaiThuoc)

        return results if dsllt else 'Chưa cập nhật'

    column_formatters = {
        'ten_nguoidangki': _traCuuLSBenhNhan_benhnhan_formatter,
        'lichkham.ngaykham': _traCuuLSBenhNhan_lichkham_formatter,
        'dslieuluongthuoc': _traCuuLSBenhNhan_dslieuluongthuoc_formatter,
    }

    can_edit = False
    can_delete = False
    can_create = False


class AuthenticatedBacSiTraCuuLSBenhNhan(CustomBacSiTraCuuLSBenhNhanView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.BAC_SI


class MyTraCuuLSBenhNhanView(AuthenticatedBacSiTraCuuLSBenhNhan):
    pass


class CustomThuNganHoaDonThanhToanView(ModelView):
    pass


class AuthenticatedThuNganHoaDonThanhToan(CustomThuNganHoaDonThanhToanView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.THU_NGAN


def count_down_with_separator(nums, separator, step):
    result = ""
    for i in range(len(nums) - 1, -1, -1):
        result = nums[i] + result
        if (len(nums) - i) % step == 0 and i != 0:
            result = separator + result
    return result


class MyHoaDonThanhToanView(AuthenticatedThuNganHoaDonThanhToan):
    column_list = ['id', 'phieukhambenh.sdt', 'phieukhambenh.lichkham.ngaykham', 'phieukhambenh.ten_nguoikham',
                   'tienkham', 'tienthuoc',
                   'tongcong', 'thanhtoan']

    column_labels = {'id': 'Mã hóa đơn', 'phieukhambenh.sdt': 'Số điện thoại',
                     'phieukhambenh.lichkham.ngaykham': 'Ngày khám',
                     'phieukhambenh.ten_nguoikham': 'Tên người khám', 'tienkham': 'Tiền khám',
                     'tienthuoc': 'Tiền thuốc', 'tongcong': 'Tổng cộng', 'thanhtoan': 'Thanh toán'}  # Đổi tên trường

    column_filters = {'phieukhambenh.lichkham.ngaykham'}
    column_searchable_list = {'phieukhambenh.sdt'}

    def _hoadonthanhtoan_tienkham_fommater(view, context, model, name):
        return count_down_with_separator(str(int(model.tienkham)), ',', 3) if model.tienkham else 'Chưa cập nhật'

    def _hoadonthanhtoan_tienthuoc_fommater(view, context, model, name):
        return count_down_with_separator(str(int(model.tienthuoc)), ',', 3) if model.tienthuoc else 'Chưa cập nhật'

    def _hoadonthanhtoan_tongcong_fommater(view, context, model, name):
        return count_down_with_separator(str(int(model.tongcong)), ',', 3) if model.tongcong else 'Chưa cập nhật'

    def _format_pay_now(view, context, model, name):
        if model.trangthai != 0:
            return 'Đã thanh toán'

        # render a form with a submit button for student, include a hidden field for the student id
        # note how checkout_view method is exposed as a route below
        else:
            _html = '''
            <form action="/admin/hoadonthanhtoan/phuongthucthanhtoan" method="POST">
                <input id="benhnhan_id" name="benhnhan_id"  type="hidden" value="{benhnhan_id}">
                <input id="hoadonthanhtoan_id" name="hoadonthanhtoan_id"  type="hidden" value="{hoadonthanhtoan_id}">
                <button style="color : white ; background-color : red ;" value="Momo" name="payUrl" type='submit'>Thanh toán
                </button>
            </form
           '''.format(hoadonthanhtoan_id=model.id, benhnhan_id=model.benhnhan_id)
        return Markup(_html)

    column_formatters = {
        'thanhtoan': _format_pay_now,
        'tienkham': _hoadonthanhtoan_tienkham_fommater,
        'tienthuoc': _hoadonthanhtoan_tienthuoc_fommater,
        'tongcong': _hoadonthanhtoan_tongcong_fommater,
    }

    can_create = False
    can_edit = False
    can_delete = False


class MyAdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html', stats=utils.MedicineReport())


class StatsView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/stats.html')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.ADMIN


admin = Admin(app=app, name='QUẢN TRỊ DANH SÁCH KHÁM BỆNH', template_mode='bootstrap4', index_view=MyAdminIndex())
# Admin
admin.add_view(MyManagerView(Manager, db.session, name='Quản Lí Nhân Sự'))
admin.add_view(MyConfigView(Config, db.session, name='Cấu hình dữ liệu'))
admin.add_view(StatsView(name='Stats'))
# Bac si
admin.add_view(MyThuocView(LoaiThuoc, db.session, name='Loại Thuốc'))
admin.add_view(MyTraCuuLSBenhNhanView(PhieuKhamBenh, db.session, name='Tra Cứu Lịch Sử Bệnh Nhân'))
admin.add_view(MyLPKView(name='Lập Phiếu Khám', endpoint='lpk'))
# Yta
admin.add_view(MyDanhSachKhamBenhView(DanhSachKhamBenh, db.session, name='Danh Sách Khám Bệnh'))
admin.add_view(MyBenhNhanView(BenhNhan, db.session, name='Tra Cứu Bệnh Nhân'))
admin.add_view(MyDKKBView(name='Đăng Kí Lịch Khám', endpoint='dkkb'))
# Thu ngan
admin.add_view(MyHoaDonThanhToanView(HoaDonThanhToan, db.session, name="Thanh Toán Hóa Đơn"))
# general
admin.add_view(MyLogoutView(name='Đăng xuất'))
