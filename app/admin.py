from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask_admin.form.upload import ImageUploadField
from app import app, db, admin, dao
from flask_login import logout_user, current_user
from flask import redirect
from app.models import BenhNhan, ChiTietBenhNhan, LichKham, DanhSachKhamBenh, Favor, Address, CMND, BHYT, UserRoleEnum, \
    Manager, Config
import os
from datetime import datetime
import cloudinary
from cloudinary.uploader import upload
from wtforms.validators import InputRequired, DataRequired
from wtforms import SelectField, PasswordField, validators, SearchField, DateField, StringField
from sqlalchemy.exc import IntegrityError

cloudinary.config(
    cloud_name="diwxda8bi",
    api_key="358748635141677",
    api_secret="QBGsplvCUjvxqZFWkpQBWKFT91I"
)


class AuthenticatedUser(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class CustomAdminManagerModelView(ModelView):
    form_create_rules = [
        'ten_quantri', 'username', 'password', 'gioitinh', 'cmnd', 'sdt', 'ngaysinh', 'hinhanh', 'diachi', 'user_role'
    ]

    column_labels = {'ten_quantri': 'Họ và tên', 'username': 'Tên người dùng', 'password': 'Mật khẩu',
                     'gioitinh': 'Giới tính', 'hinhanh': 'Hình ảnh',
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


class AuthenticatedAdminManager(CustomAdminManagerModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.ADMIN


class AuthenticatedAdminConfig(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.ADMIN


class MyManagerView(AuthenticatedAdminManager):
    column_list = ['id', 'username', 'ten_quantri', 'gioitinh', 'cmnd', 'sdt', 'ngaysinh', 'hinhanh', 'diachi',
                   'user_role']
    column_searchable_list = ['id', 'ten_quantri', 'gioitinh', 'cmnd', 'sdt', 'ngaysinh', 'hinhanh', 'diachi',
                              'user_role']
    can_create = True
    can_delete = True
    can_edit = True


class MyConfigView(AuthenticatedAdminConfig):
    column_list = ['id', 'key', 'value']
    column_searchable_list = ['key', 'value']
    can_edit = True
    can_create = True


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
                                                             validators.Regexp(r'^\d+$', message='Must be a number')]),
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
        import hashlib
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
    # def edit_model(self, form, model):
    #     pass

    def on_model_change(self, form, model, is_created):
        super().on_model_change(form, model, is_created)

        bn = dao.get_benhnhan_by_id(model.id)
        ctbn = dao.get_chitietbenhnhan_by_benhnhan_id(bn.id)

        sdt = getattr(model, 'chitietbenhnhan.sdt')
        so_cmnd = getattr(model, 'chitietbenhnhan.cmnd')
        so_bhyt = getattr(model, 'chitietbenhnhan.bhyt')

        existing_sdt = dao.get_chitietbenhnhan_by_sdt(sdt)
        existing_cmnd = dao.get_cmnd_by_soCMND(so_cmnd)
        existing_bhyt = dao.get_bhyt_by_soBHYT(so_bhyt)

        if existing_sdt:
            db.session.rollback()
            form['chitietbenhnhan.sdt'].errors.append('Số điện thoại này đã được đăng kí !')

        # Thực hiện xử lý sau khi mô hình được thay đổi
        ctbn.sdt = form['chitietbenhnhan.sdt'].data
        self.session.add(ctbn)
        self.session.commit()


class AuthenticatedYTaBenhNhan(CustomYTaBenhNhanModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.Y_TA


class MyBenhNhanView(AuthenticatedYTaBenhNhan):
    can_create = True
    can_export = True
    can_view_details = True
    can_delete = False


class MyLogoutView(AuthenticatedUser):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/admin')


if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

admin.add_view(MyDanhSachKhamBenhView(DanhSachKhamBenh, db.session))
admin.add_view(MyBenhNhanView(BenhNhan, db.session))

admin.add_view(MyManagerView(Manager, db.session))
admin.add_view(MyConfigView(Config, db.session))
admin.add_view(MyLogoutView(name='Đăng xuất'))
