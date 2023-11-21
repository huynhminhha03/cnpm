from flask import Flask, render_template, request, redirect, url_for
from app import app, login, db
from datetime import datetime
from flask_login import login_user
import dao
from app.models import BenhNhan, ChiTietBenhNhan, LichKham, DanhSachKhamBenh, Favor, Address, CMND, BHYT, UserRoleEnum

MAX_VALUE = 40

@app.route("/dat-lich-kham", methods=['GET', 'POST'])
def booking():
    user_checked = request.form.get('user_checked')
    first_checked = request.form.get('first_checked')
    print(user_checked)
    print(first_checked)

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
                                       , user_checked=user_checked, first_checked=first_checked , error=error
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

        ctbn = ChiTietBenhNhan(gioitinh=gender, sdt=phone, ngaysinh=birthday,benhnhan_id=bn.id)
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
                               , first_checked=first_checked, user_checked=user_checked, id_benhnhan=bn.id , bn=bn)

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
            if count > MAX_VALUE:
                checked = 'failed'
                return render_template('User/booking.html', check=checked, lichkham=l1
                                       , first_checked=first_checked, user_checked=user_checked, id_benhnhan=bn.id)
        elif not list:
            list = LichKham(ngaykham=date_booking)
            db.session.add(list)

        dskb = dao.get_duplicate_dangkikhambenh_by_2id(bn.id, list.id)
        if not dskb:
            dskb = DanhSachKhamBenh(benhnhan_id=bn.id, lichkham_id=list.id)
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
        return render_template('User/booking.html', check=checked, lichkham=list
                               , first_checked=first_checked, user_checked=user_checked, sdt=ctbn.sdt,
                               id_benhnhan=bn.id, bn=bn, dskb=dskb)

    checked = 'failed'
    user_checked = 'False'
    first_checked = 'False'
    return render_template('User/booking.html', check=checked
                           , first_checked=first_checked, user_checked=user_checked)


@login.user_loader
def load_benhnhan(benhnhan_id):
    return dao.get_benhnhan_by_id(benhnhan_id)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register")
def register():
    return render_template("Authentication/register.html")


@app.route("/login")
def login():
    return render_template("Authentication/login.html")


if __name__ == '__main__':
    app.run(debug=True)
