from flask import Flask, render_template, request , redirect , url_for
from app import app, login, db
from datetime import datetime
from flask_login import login_user
import dao
from app.models import BenhNhan, ChiTietBenhNhan, LichKham, DanhSachKhamBenh, DanhSachDangKiKhamBenh ,  Favor, Address, Address_temp , Favor_temp , CMND_temp , BHYT_temp ,  CMND, BHYT, UserRoleEnum


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
    cmnd_temp = request.form.get('cmnd')
    bhyt_temp = request.form.get('bhyt')
    address_temp = request.form.get('address')
    date_booking = request.form.get('booking')
    favor_temp = request.form.get('favor')


#check lich kham da ton tai chua :

    l = dao.get_lichkham_by_ngaykham(date_booking)
    if l:
        count = dao.count_danhsachdangkikhambenh_theolichkham(l.id)
        l1 = dao.get_lichkham_by_id(l.id)
        if count > 39:
            checked = 'failed'
            return render_template('booking.html', check=checked, lichkham=l1)
    elif not l:
        l = LichKham(ngaykham=date_booking)
        db.session.add(l)
        db.session.commit()

#check benh nhan dang ki 1 so dien thoai nhieu lan hay ko :

    dsdkkb_dup = dao.get_sdt_by_id_danhsachdangkikhambenh(phone)
    if dsdkkb_dup:
        l1 = dao.get_lichkham_by_id(l.id)
        checked = 'duplicate_phone_register'
        return render_template('booking.html', check=checked, lichkham=l1, dsdkkb=dsdkkb_dup)

#tao danh sach dang ki kham benh

    dsdkkb = DanhSachDangKiKhamBenh(hoten=name, sdt=phone, gioitinh=gender, ngaysinh=birthday, lichkham_id=l.id)
    db.session.add(dsdkkb)
    db.session.commit()

    #tao address tam :
    if address_temp:
        at = Address_temp(ten_diachi=address_temp,danhsachdangkikhambenh_id=dsdkkb.id)
        db.session.add(at)
        db.session.commit()

    #tao cmnd tam :
    if cmnd_temp:
        ct = CMND_temp(so_cmnd=cmnd_temp,danhsachdangkikhambenh_id=dsdkkb.id)
        db.session.add(ct)
        db.session.commit()

    #tao bhyt tam :
    if bhyt_temp:
        bt = BHYT_temp(so_bhyt=bhyt_temp,danhsachdangkikhambenh_id=dsdkkb.id)
        db.session.add(bt)
        db.session.commit()

    #tao nhu cau tam :
    if favor_temp:
        ft = Favor_temp(mongmuon=favor_temp,danhsachdangkikhambenh_id=dsdkkb.id)
        db.session.add(ft)
        db.session.commit()


    checked = 'success'
    return render_template('booking.html', check=checked)


if __name__ == '__main__':
    app.run(debug=True)
