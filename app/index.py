import hmac
import json
import requests
import uuid
from flask import render_template, url_for
from flask_login import login_user, login_required
# from twilio.rest import Client
from app import login_manager, controllers
from app.admin import *
from app.models import (LichKham, Favor, LoaiThuoc_DonViThuoc, DsLieuLuongThuoc, )

cloudinary.config(
    cloud_name="diwxda8bi",
    api_key="358748635141677",
    api_secret="QBGsplvCUjvxqZFWkpQBWKFT91I"
)

# key config
patients_per_day_key = 'patients_per_day'
medical_expenses_key = 'medical_expenses'
number_of_per_pack_key = 'number_of_per_pack'

# global variable
today = datetime.now().strftime('%Y-%m-%d')


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


@app.route('/editProfileManager', methods=['POST'])
def editProfileManager():
    currentpw = request.form.get('currentpw')
    newpw = request.form.get('newpw')
    manager_id = request.form.get('manager_id')
    if currentpw and newpw:
        manager = dao.get_manager_by_id(manager_id)
        hashcode_currentpw = str(hashlib.md5(currentpw.strip().encode('utf-8')).hexdigest())
        if manager.password.__eq__(hashcode_currentpw):
            manager.password = str(hashlib.md5(newpw.encode('utf-8')).hexdigest())
            db.session.add(manager)
            db.session.commit()
            return redirect(url_for('admin_index', success='success'))

        else:
            return redirect(url_for('admin_index', failed='failed'))

    return redirect('/admin')


@app.route('/admin')
def admin_index():
    return MyAdminIndex().render('/admin/index.html')


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
        # client = Client(app.config['TWILIO_ACCOUNT_SID'], app.config['TWILIO_AUTH_TOKEN'])

        # message = client.messages.create(
        #     body=f'Số điện thoại {ctbn.sdt} đã đặt lịch vào ngày {list.ngaykham.strftime("%d/%m/%Y")} thành công ! ',
        #     from_='(330) 299-7281',
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
    today = datetime.now().strftime('%Y-%m-%d')

    dsloaithuoc = dao.load_loaithuoc()
    dsdonvithuoc = dao.load_donvithuoc()

    ten_nguoikham = request.form.get('name_patients')
    sdt = request.form.get('phone')
    ngaykham = request.form.get('booking')
    trieuchung = request.form.get('symptom')
    dudoanbenh = request.form.get('predict-disease-type')

    existing_sdt = dao.get_chitietbenhnhan_by_sdt(sdt)

    if not existing_sdt:
        error = "not_existing_phone"
        return render_template("admin/medical_report.html", sdt=sdt, error=error, today=today
                               , loaithuoc=dsloaithuoc, donvithuoc=dsdonvithuoc)

    ctbn = dao.get_chitietbenhnhan_by_sdt(sdt)
    lichkham = dao.get_lichkham_by_ngaykham(ngaykham)
    bn = dao.get_benhnhan_by_id(ctbn.benhnhan_id)
    config_number_of_per_pack = int(dao.get_value_by_key(number_of_per_pack_key).value)

    dskb = None

    if not lichkham or not bn:
        error = "not_existing_dskb"
        return render_template("admin/medical_report.html", sdt=sdt, ngaykham=ngaykham, error=error, today=today,
                               loaithuoc=dsloaithuoc, donvithuoc=dsdonvithuoc)
    else:
        dskb = dao.get_danhsachkhambenh_by_lichkham_and_benhnhan(lichkham=lichkham, benhnhan=bn)

    if not dskb:
        error = "not_existing_dskb"
        return render_template("admin/medical_report.html", sdt=sdt, ngaykham=ngaykham, error=error, today=today)

    phieukhambenh = PhieuKhamBenh(ten_nguoikham=ten_nguoikham, sdt=sdt, trieuchung=trieuchung, dudoanbenh=dudoanbenh,
                                  ngaylapphieukham=datetime.now(), lichkham_id=lichkham.id, benhnhan_id=bn.id)

    db.session.add(phieukhambenh)
    db.session.commit()

    medicine = request.form.getlist('medicine')
    unit = request.form.getlist('unit')
    number = request.form.getlist('number')
    using = request.form.getlist('using')

    lenght = len(medicine)
    for i in range(lenght):
        loaithuoc = dao.get_loaithuoc_by_tenloaithuoc(medicine[i])
        donvithuoc = dao.get_donvithuoc_by_tendonvithuoc(unit[i])
        loaithuoc_donvithuoc = dao.get_loaithuoc_donvithuoc_by_2id(loaithuoc, donvithuoc)

        vien = dao.get_donvithuoc_by_tendonvithuoc('Viên')
        soTienCuaMotVien = dao.get_loaithuoc_donvithuoc_by_2id(loaithuoc, vien).giatien

        if not loaithuoc_donvithuoc and unit[i] == 'Vỉ':
            loaithuoc_donvithuoc = LoaiThuoc_DonViThuoc(loaithuoc_id=loaithuoc.id, donvithuoc_id=donvithuoc.id
                                                        , giatien=soTienCuaMotVien * config_number_of_per_pack)
            db.session.add(loaithuoc_donvithuoc)
            db.session.commit()
        elif loaithuoc_donvithuoc and unit[i] == 'Vỉ':
            loaithuoc_donvithuoc.giatien = soTienCuaMotVien * config_number_of_per_pack
            db.session.add(loaithuoc_donvithuoc)
            db.session.commit()

        dsLieuLuongThuoc = DsLieuLuongThuoc(loaithuoc_donvithuoc_id=loaithuoc_donvithuoc.id, soluong=int(number[i])
                                            , cachdung=using[i], phieukhambenh_id=phieukhambenh.id)
        db.session.add(dsLieuLuongThuoc)
        db.session.commit()

    dslt = dao.get_dsLieuLuongThuoc_by_phieuKhamBenh_id(phieukhambenh.id)
    hoadonthanhtoan = HoaDonThanhToan()
    hoadonthanhtoan.id = str(uuid.uuid4())
    hoadonthanhtoan.ngaylaphoadon = today
    tienkham = float(dao.get_value_by_key(medical_expenses_key).value)
    hoadonthanhtoan.tienkham = tienkham
    tienthuoc = 0
    for d in dslt:
        loaithuoc_donvithuoc = dao.get_loaithuoc_donvithuoc_by_id(d.loaithuoc_donvithuoc_id)
        tienthuoc += loaithuoc_donvithuoc.giatien * d.soluong
    hoadonthanhtoan.tienthuoc = tienthuoc
    hoadonthanhtoan.tongcong = tienkham + tienthuoc
    hoadonthanhtoan.benhnhan_id = bn.id
    hoadonthanhtoan.phieukhambenh_id = phieukhambenh.id
    db.session.add(hoadonthanhtoan)
    db.session.commit()

    error = 'None'
    return render_template("admin/medical_report.html", error=error, today=today
                           , loaithuoc=dsloaithuoc, donvithuoc=dsdonvithuoc)


@app.route('/logout_manager')
@login_required
def logout_manager():
    logout_user()
    return redirect('/admin')


@app.route('/admin/hoadonthanhtoan/phuongthucthanhtoan', methods=['GET', 'POST'])
@login_required
def phuongthucthanhtoan():
    hoadonthanhtoan = dao.get_hoadonthanhtoan_by_id(request.form.get('hoadonthanhtoan_id'))
    bn = dao.get_benhnhan_by_id(request.form.get('benhnhan_id'))
    ctbn = dao.get_chitietbenhnhan_by_benhnhan_id(bn.id)
    phieukhambenh = dao.get_phieukhambenh_by_id(hoadonthanhtoan.phieukhambenh_id)
    diachi = dao.get_diachi_by_ctbn_id(ctbn.id)
    bhyt = dao.get_bhyt_by_ctbn_id(ctbn.id)
    dsllt = dao.get_dsLieuLuongThuoc_by_phieuKhamBenh_id(phieukhambenh.id)
    tienkham = float(dao.get_value_by_key(medical_expenses_key).value)
    length = len(dsllt)
    array_lt_dvt = []
    array_loaithuoc = []
    array_donvithuoc = []
    for d in dsllt:
        loaithuoc_donvithuoc = dao.get_loaithuoc_donvithuoc_by_id(d.loaithuoc_donvithuoc_id)
        loaithuoc = dao.get_loaithuoc_by_id(loaithuoc_donvithuoc.loaithuoc_id)
        donvithuoc = dao.get_donvithuoc_by_id(loaithuoc_donvithuoc.donvithuoc_id)
        array_lt_dvt.append(loaithuoc_donvithuoc)
        array_loaithuoc.append(loaithuoc)
        array_donvithuoc.append(donvithuoc)
    return render_template('admin/payment.html', hoadonthanhtoan=hoadonthanhtoan, bn=bn
                           , ctbn=ctbn, pkb=phieukhambenh, diachi=diachi, bhyt=bhyt, dsllt=dsllt,
                           loaithuocs=array_loaithuoc, donvithuocs=array_donvithuoc, lt_dvts=array_lt_dvt,
                           length=length, tienkham=tienkham)


@app.route('/admin/hoadonthanhtoan/phuongthucthanhtoan/checkout', methods=['GET', 'POST'])
@login_required
def checkout_view():
    hoadonthanhtoan = dao.get_hoadonthanhtoan_by_id(request.form.get('hoadonthanhtoan_id'))

    if 'payUrl' in request.form and request.method == "POST":
        # parameters send to MoMo get get payUrl
        endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
        partnerCode = "MOMO"
        accessKey = "F8BBA842ECF85"
        secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
        orderInfo = "pay with MoMo"
        redirectUrl = "http://127.0.0.1:5000/payment"
        ipnUrl = "http://127.0.0.1:5000/payment"
        amount = str(int(hoadonthanhtoan.tongcong))
        orderId = hoadonthanhtoan.id
        requestId = str(uuid.uuid4())
        requestType = "captureWallet"
        extraData = ""  # pass empty value or Encode base64 JsonString

        # before sign HMAC SHA256 with format: accessKey=$accessKey&amount=$amount&extraData=$extraData&ipnUrl
        # =$ipnUrl &orderId=$orderId&orderInfo=$orderInfo&partnerCode=$partnerCode&redirectUrl=$redirectUrl
        # &requestId=$requestId &requestType=$requestType
        rawSignature = "accessKey=" + accessKey + "&amount=" + amount + "&extraData=" + extraData + "&ipnUrl=" + ipnUrl + "&orderId=" + orderId + "&orderInfo=" + orderInfo + "&partnerCode=" + partnerCode + "&redirectUrl=" + redirectUrl + "&requestId=" + requestId + "&requestType=" + requestType

        # puts raw signature
        # print("--------------------RAW SIGNATURE----------------")
        # print(rawSignature)
        # signature
        h = hmac.new(bytes(secretKey, 'ascii'), bytes(rawSignature, 'ascii'), hashlib.sha256)
        signature = h.hexdigest()

        # json object send to MoMo endpoint

        data = {
            'partnerCode': partnerCode,
            'partnerName': "Test",
            'storeId': "MomoTestStore",
            'requestId': requestId,
            'amount': amount,
            'orderId': orderId,
            'orderInfo': orderInfo,
            'redirectUrl': redirectUrl,
            'ipnUrl': ipnUrl,
            'lang': "vi",
            'extraData': extraData,
            'requestType': requestType,
            'signature': signature
        }

        data = json.dumps(data)  # Convert from Dict to str
        clen = len(data)

        response = requests.post(endpoint, data=data,
                                 headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})

        return redirect(response.json()['payUrl'])
    elif 'tienmat' in request.form and request.method == "POST":
        hoadonthanhtoan.trangthai = 1
        db.session.add(hoadonthanhtoan)
        db.session.commit()
        return redirect('/admin/hoadonthanhtoan')
    else:
        return hoadonthanhtoan


@app.route('/payment', methods=['GET'])
@login_required
def payment_results():
    resultCode = request.args.get('resultCode')
    orderId = request.args.get('orderId')
    hoadonthanhtoan = dao.get_hoadonthanhtoan_by_id(orderId)
    if resultCode == '0':  # 'get para là resultCode , nếu = 0 là thành công , != là thất bại'
        present_url = request.url
        controllers.momopayment(presentUrl=present_url)
        hoadonthanhtoan.ngaythanhtoanhoadon = today
        hoadonthanhtoan.trangthai = 1
        db.session.add(hoadonthanhtoan)
        db.session.commit()
        return redirect('/admin/hoadonthanhtoan')
    else:
        hoadonthanhtoan.id = str(uuid.uuid4())  # cập nhật lại id tự sinh của uuid nếu thất bại
        db.session.add(hoadonthanhtoan)
        db.session.commit()
        return redirect('/admin/hoadonthanhtoan')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
