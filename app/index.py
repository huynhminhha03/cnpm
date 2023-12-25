from flask import Flask, render_template, request, redirect, url_for
from app import app, login_manager, db
from twilio.rest import Client
import dao
from app.models import BenhNhan, ChiTietBenhNhan, LichKham, DanhSachKhamBenh, Favor, Address, CMND, BHYT, UserRoleEnum
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import cloudinary
import cloudinary.uploader
from admin import *

cloudinary.config(
    cloud_name="diwxda8bi",
    api_key="358748635141677",
    api_secret="QBGsplvCUjvxqZFWkpQBWKFT91I"
)

# key config
patients_per_day_key = 'patients_per_day'
medical_expenses_key = 'medical_expenses'


@app.route("/dat-lich-kham", methods=['GET', 'POST'])
def booking():
    user_checked = request.form.get('user_checked')
    first_checked = request.form.get('first_checked')

    checked = None
    if request.method == "GET":
        user_checked = 'False'
        first_checked = 'False'

        return render_template("Authentication/authenUser.html"
                               , user_checked=user_checked, first_checked=first_checked
                               )
    elif request.method == "POST" and first_checked == 'False' and user_checked == 'False':

        first_checked = 'True'
        name_auth = request.form.get('name_patients_auth')
        phone_auth = request.form.get('phone_auth')

        ctbn = dao.get_chitietbenhnhan_by_sdt(phone_auth)
        bn = None
        if phone_auth and not ctbn:
            return render_template("User/registerUserForm.html"
                                   , first_checked=first_checked, user_checked=user_checked, phone=phone_auth,
                                   name=name_auth)
        elif phone_auth and ctbn:
            bn = dao.get_benhnhan_by_id(ctbn.id)
            if bn.ten_benhnhan == name_auth and ctbn.sdt == phone_auth:
                user_checked = 'True'
                return render_template("User/booking.html",
                                       first_checked=first_checked, user_checked=user_checked, id_benhnhan=bn.id, bn=bn)
            else:
                first_checked = 'False'
                user_checked = 'False'
                error = 'name_phone_is_not_matched'
                return render_template("Authentication/authenUser.html"
                                       , user_checked=user_checked, first_checked=first_checked, error=error
                                       )

    elif request.method == "POST" and first_checked == 'True' and user_checked == 'False':

        name = request.form.get('name_patients')
        birthday = request.form.get('birthday')
        gender = request.form.get('gender')
        phone = request.form.get('phone')
        cmnd = request.form.get('cmnd')
        bhyt = request.form.get('bhyt')
        address = request.form.get('address')

        if cmnd and dao.get_cmnd_by_soCMND(cmnd):
            user_checked = 'False'
            error = 'dup_cmnd'
            return render_template("User/registerUserForm.html"
                                   , first_checked=first_checked, user_checked=user_checked, phone=phone, name=name,
                                   birthday=birthday, error=error, cmnd=cmnd)

        if bhyt and dao.get_bhyt_by_soBHYT(bhyt):
            user_checked = 'False'
            error = 'dup_bhyt'
            return render_template("User/registerUserForm.html"
                                   , first_checked=first_checked, user_checked=user_checked, phone=phone, name=name,
                                   birthday=birthday, error=error, bhyt=bhyt)

        bn = BenhNhan(ten_benhnhan=name, user_role=UserRoleEnum.BENH_NHAN)
        db.session.add(bn)
        db.session.commit()

        ctbn = ChiTietBenhNhan(gioitinh=gender, sdt=phone, ngaysinh=birthday, benhnhan_id=bn.id)
        db.session.add(ctbn)

        if cmnd and not dao.get_cmnd_by_soCMND(cmnd):
            c = CMND(so_cmnd=cmnd, chitiet_benhnhan_id=ctbn.id)
            db.session.add(c)

        if bhyt and not dao.get_bhyt_by_soBHYT(bhyt):
            bhyt = BHYT(so_bhyt=bhyt, chitiet_benhnhan_id=ctbn.id)
            db.session.add(bhyt)

        if address:
            a = Address(ten_diachi=address, chitiet_benhnhan_id=ctbn.id)
            db.session.add(a)

        db.session.commit()

        user_checked = 'True'
        return render_template("User/Booking.html"
                               , first_checked=first_checked, user_checked=user_checked, id_benhnhan=bn.id, bn=bn)

    elif request.method == "POST" and first_checked == 'True' and user_checked == 'True':

        favor = request.form.get('favor')
        date_booking = request.form.get('booking')
        id_bn = int(request.form.get('id_benhnhan'))

        bn = dao.get_benhnhan_by_id(id_bn)
        list = dao.get_lichkham_by_ngaykham(date_booking)
        ctbn = dao.get_chitietbenhnhan_by_benhnhan_id(id_bn)

        if list:
            count = dao.count_danhsachkhambenh_theo_lichkham(list.id)
            l1 = dao.get_lichkham_by_id(list.id)
            config_max_patient = dao.get_value_by_key(patients_per_day_key)
            print(count)
            print(int(config_max_patient.value))
            if count >= int(config_max_patient.value):
                checked = 'failed'
                return render_template('User/booking.html', check=checked, lichkham=l1
                                       , first_checked=first_checked, user_checked=user_checked, id_benhnhan=bn.id,
                                       bn=bn)
        elif not list:
            list = LichKham(ngaykham=date_booking)
            db.session.add(list)

        dskb = dao.get_duplicate_dangkikhambenh_by_2id(bn.id, list.id)
        count = dao.count_danhsachkhambenh_theo_lichkham(list.id)

        if not dskb:
            stt = count + 1
            dskb = DanhSachKhamBenh(stt=stt, benhnhan_id=bn.id, lichkham_id=list.id)
            db.session.add(dskb)
        else:
            checked = 'duplicate_phone_register'
            return render_template('User/booking.html', check=checked, lichkham=list
                                   , first_checked=first_checked, user_checked=user_checked, sdt=ctbn.sdt,
                                   id_benhnhan=bn.id, bn=bn, dskb=dskb)

        if favor:
            f = Favor(mongmuon=favor, chitiet_benhnhan_id=ctbn.id)
            db.session.add(f)

        db.session.commit()

        checked = 'success'
        client = Client(app.config['TWILIO_ACCOUNT_SID'], app.config['TWILIO_AUTH_TOKEN'])

        # message = client.messages.create(
        #     body=f'Số điện thoại {ctbn.sdt} đã đặt lịch vào ngày {list.ngaykham.strftime("%d/%m/%Y")} thành công ! ',
        #     from_='+13302997281',
        #     to=f'+84{ctbn.sdt[1:]}'
        # )

        return render_template('User/booking.html', check=checked, lichkham=list
                               , first_checked=first_checked, user_checked=user_checked, sdt=ctbn.sdt,
                               id_benhnhan=bn.id, bn=bn, dskb=dskb)

    checked = 'failed'
    user_checked = 'False'
    first_checked = 'False'
    return render_template('User/booking.html', check=checked
                           , first_checked=first_checked, user_checked=user_checked)


@login_manager.user_loader
def load_manager(manager_id):
    return dao.get_manager_by_id(manager_id)


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/admin/login', methods=['post'])
def login_admin_process():
    username = request.form.get('username')
    password = request.form.get('password')

    user = dao.auth_manager(username=username, password=password)
    if user:
        login_user(user=user)

    return redirect('/admin')


@app.errorhandler(401)
def unauthorized(e):
    return render_template('Authentication/authenDeny.html'), 401


@app.route("/admin/dkkb", methods=['GET'])
@login_required
def examination():
    return render_template("admin/medical_examination.html")


@app.route('/admin/dkkb', methods=['POST'])
def yta_examination():
    sdt = request.form.get('phone')
    date_booking = request.form.get('booking')
    favor = request.form.get('favor')
    list = dao.get_lichkham_by_ngaykham(date_booking)

    ctbn = dao.get_chitietbenhnhan_by_sdt(sdt)

    if not ctbn:
        check = 'phone_not_found'
        return render_template('admin/medical_examination.html', check=check, sdt=sdt)

    bn = dao.get_benhnhan_by_id(ctbn.benhnhan_id)

    if list:
        count = dao.count_danhsachkhambenh_theo_lichkham(list.id)
        l1 = dao.get_lichkham_by_id(list.id)
        config_max_patient = dao.get_value_by_key(patients_per_day_key)
        print(count)
        print(int(config_max_patient.value))
        if count >= int(config_max_patient.value):
            check = 'failed'
            return render_template('admin/medical_examination.html', check=check, lichkham=l1
                                   , id_benhnhan=bn.id, bn=bn)
    elif not list:
        list = LichKham(ngaykham=date_booking)
        db.session.add(list)

    dskb = dao.get_duplicate_dangkikhambenh_by_2id(bn.id, list.id)
    count = dao.count_danhsachkhambenh_theo_lichkham(list.id)

    if not dskb:
        stt = count + 1
        dskb = DanhSachKhamBenh(stt=stt, benhnhan_id=bn.id, lichkham_id=list.id)
        db.session.add(dskb)
    else:
        checked = 'duplicate_phone_register'
        return render_template('admin/medical_examination.html', check=checked, lichkham=list
                               , sdt=ctbn.sdt,
                               id_benhnhan=bn.id, bn=bn, dskb=dskb)

    if favor:
        f = Favor(mongmuon=favor, chitiet_benhnhan_id=ctbn.id)
        db.session.add(f)

    db.session.commit()

    checked = 'success'
    return render_template('admin/medical_examination.html', check=checked, id_benhnhan=bn.id)


@app.route("/admin/lpk", methods=['POST'])
def bacsi_medical_report():
    ten_benhnhan = request.form.get('name_patients')
    sdt = request.form.get('phone')
    ngaykham = request.form.get('booking')
    trieuchung = request.form.get('symptom')
    dudoanbenh = request.form.get('predict-disease-type')

    today = datetime.now().strftime('%Y-%m-%d')

    existing_sdt = dao.get_chitietbenhnhan_by_sdt(sdt)
    if not existing_sdt:
        error = "not_existing_phone"
        return render_template("admin/medical_report.html", sdt=sdt, error=error, today=today)

    ctbn = dao.get_chitietbenhnhan_by_sdt(sdt)
    lichkham = dao.get_lichkham_by_ngaykham(ngaykham)
    bn = dao.get_benhnhan_by_id(ctbn.benhnhan_id)
    dskb = dao.get_danhsachkhambenh_by_lichkham_and_benhnhan(lichkham=lichkham, benhnhan=bn)
    if not dskb:
        error = "not_existing_dskb"
        return render_template("admin/medical_report.html", sdt=sdt, ngaykham=ngaykham, error=error, today=today)

    error = 'None'
    return render_template("admin/medical_report.html", error=error)


@app.route('/logout_manager')
@login_required
def logout_manager():
    logout_user()
    return redirect('/admin')


if __name__ == '__main__':
    app.run(debug=True)
