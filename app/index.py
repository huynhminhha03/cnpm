from flask import Flask, render_template, request , redirect , url_for
from app import app, login, db
from datetime import datetime
from flask_login import login_user
import dao
from app.models import BenhNhan, ChiTietBenhNhan, LichKham, DanhSachKhamBenh ,  Favor, Address, CMND, BHYT, UserRoleEnum


@app.route("/dat-lich-kham")
def booking():
    return render_template("booking.html")


@login.user_loader
def load_benhnhan(benhnhan_id):
    return dao.get_benhnhan_by_id(benhnhan_id)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route('/register-process', methods=['post'])
def register_processing():
    checked = ""
    name = request.form.get('name_patients')
    birthday = request.form.get('birthday')
    gender = request.form.get('gender')
    phone = request.form.get('phone')
    booking = request.form.get('booking')

    bn = dao.get_duplicate_benhnhan_name_by_sdt(name, phone)
    l = dao.get_lichkham_by_ngaykham(booking)


    if l:
        count = dao.count_danhsachkhambenh_theolichkham(l.id)
        l1 = dao.get_lichkham_by_id(l.id)
        if count > 39:
            checked = 'failed'
            return render_template('booking.html', check=checked , lichkham=l1)
    elif not l:
        l = LichKham(ngaykham=booking)
        db.session.add(l)
        db.session.commit()


    if not bn:
        bn = BenhNhan(ten_benhnhan=name, sdt=phone,user_role=UserRoleEnum.BENH_NHAN)
        db.session.add(bn)
        db.session.commit()

        bn_ct = ChiTietBenhNhan(gioitinh=gender, ngaysinh=birthday, benhnhan_id=bn.id)
        db.session.add(bn_ct)
        db.session.commit()
    else:
        bn_ct = dao.get_chitietbenhnhan_by_benhnhan_id(bn.id)

    address = request.form.get('address')
    address_check = dao.get_chitietbenhnhan_by_address(bn_ct.id,address)
    if address and not address_check:
        ad = Address(ten_diachi=address, chitiet_benhnhan_id=bn_ct.id)
        db.session.add(ad)
        db.session.commit()

    # cmnd = request.form.get('cccd')
    # cmnd_check = dao.get_cmnd_by_soCMND(cmnd)
    # if cmnd and not cmnd_check:
    #     cc = CMND(so_cmnd=cmnd, chitiet_benhnhan_id=bn_ct.id)
    #     db.session.add(cc)
    #     db.session.commit()
    #
    #
    # bhyt = request.form.get('bhyt')
    # bhyt_check = dao.get_bhyt_by_soBHYT(bhyt)
    # if bhyt and not bhyt_check:
    #     bh = BHYT(so_bhyt=bhyt, chitiet_benhnhan_id=bn_ct.id)
    #     db.session.add(bh)
    #     db.session.commit()
    #
    #
    #
    # favor = request.form.get('favor')
    # if favor:
    #     fa = Favor(mongmuon=favor, chitiet_benhnhan_id=bn_ct.id)
    #     db.session.add(fa)
    #     db.session.commit()
    #
    # dskb = DanhSachKhamBenh(user_id=bn.id, lichkham_id=l.id)
    # db.session.add(dskb)
    # db.session.commit()
    # checked = 'success'

    return render_template('booking.html', check = checked)


if __name__ == '__main__':
    app.run(debug=True)