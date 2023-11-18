from flask import Flask, render_template, request , redirect , url_for
from app import app, login, db
import datetime
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
    name = request.form.get('name_patients')
    birthday = request.form.get('birthday')
    gender = request.form.get('gender')
    phone = request.form.get('phone')
    booking = request.form.get('booking')

    bn = BenhNhan(name_patients=name, user_role=UserRoleEnum.BENH_NHAN)
    db.session.add(bn)
    db.session.commit()

    bn_ct = ChiTietBenhNhan(sdt=phone, gioitinh=gender, ngaysinh=birthday, user_id=bn.id)
    db.session.add(bn_ct)
    db.session.commit()

    l = dao.get_lichkham_by_ngaykham(booking)

    if not l:
        l = LichKham(ngaykham=booking)
        db.session.add(l)
        db.session.commit()

    dskb = DanhSachKhamBenh(user_id=bn.id,lichkham_id=l.id)
    db.session.add(dskb)
    db.session.commit()

    address = request.form.get('address')
    if address:
        ad = Address(ten_diachi=address, chitiet_benhnhan_id=bn_ct.id)
        db.session.add(ad)
        db.session.commit()

    cccd = request.form.get('cccd')
    if cccd:
        cc = CMND(so_cmnd=cccd, chitiet_benhnhan_id=bn_ct.id)
        db.session.add(cc)
        db.session.commit()

    bhyt = request.form.get('bhyt')
    if bhyt:
        bh = BHYT(so_bhyt=bhyt, chitiet_benhnhan_id=bn_ct.id)
        db.session.add(bh)
        db.session.commit()

    favor = request.form.get('favor')
    if favor:
        fa = Favor(mongmuon=favor, chitiet_benhnhan_id=bn_ct.id)
        db.session.add(fa)
        db.session.commit()

    checked = 'success'

    return render_template('booking.html' , check = checked)


if __name__ == '__main__':
    app.run(debug=True)
