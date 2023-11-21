from flask import Flask, render_template, request, redirect
from app import controllers , app
import uuid
import json, hmac, hashlib, requests
from flask_login import LoginManager
from app.models import BenhNhan,ChiTietBenhNhan,CMND,BHYT


login = LoginManager(app)

@login.user_loader
def load_user(id):
    return BenhNhan.query.get(id)

@app.route('/')
def home():
    return render_template('payment/info.html')


@app.route('/payment-success', methods=['GET'])
def payment_success():
    present_url = request.url
    controllers.momopayment(presentUrl=present_url)
    return render_template("payment/thanks.html")


@app.route('/online-checkout', methods=['GET', 'POST'])
def online_checkout():
    if 'payUrl' in request.form:
        # parameters send to MoMo get get payUrl
        endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
        partnerCode = "MOMO"
        accessKey = "F8BBA842ECF85"
        secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
        orderInfo = "pay with MoMo"
        redirectUrl = "http://127.0.0.1:5000/payment-success"  # Return when successfully payment  http://127.0.0.1:5000/thanks
        ipnUrl = "http://127.0.0.1:5000/payment-success"  # Return the result payment
        amount = request.form.get('price')
        orderId = str(uuid.uuid4())
        requestId = str(uuid.uuid4())
        requestType = "captureWallet"
        extraData = ""  # pass empty value or Encode base64 JsonString

        # before sign HMAC SHA256 with format: accessKey=$accessKey&amount=$amount&extraData=$extraData&ipnUrl=$ipnUrl
        # &orderId=$orderId&orderInfo=$orderInfo&partnerCode=$partnerCode&redirectUrl=$redirectUrl&requestId=$requestId
        # &requestType=$requestType
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

    elif 'submit' in request.form:
        # choice = request.form.get('submit', 'VNPay')
        price = request.form.get('price')
        # choice_content = f'Choose button {choice}'
        # choice_content = f'Product has price is {price}'
        presentUrl = request.url
        choice_content = f'The present Url is {presentUrl}'
        return render_template('payment/online-checkout.html', choice_content=choice_content)


if __name__ == '__main__':
    app.run(debug=True)






