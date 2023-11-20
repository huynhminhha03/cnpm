from .models import MomoPayment
from . import db
from urllib.parse import urlparse, parse_qs


def momopayment(presentUrl):
    parsed_url = urlparse(presentUrl)
    query_params = parse_qs(parsed_url.query)

    if 'partnerCode' in query_params and query_params['partnerCode'][0] == 'MOMO':
        partnerCode = query_params.get('partnerCode', [''])[0]
        orderId = query_params.get('orderId', [''])[0]
        requestId = query_params.get('requestId', [''])[0]
        amount = query_params.get('amount', [''])[0]
        orderInfo = query_params.get('orderInfo', [''])[0]
        orderType = query_params.get('orderType', [''])[0]
        transId = query_params.get('transId', [''])[0]
        payType = query_params.get('payType', [''])[0]
        signature = query_params.get('signature', [''])[0]


    new_mompayment = MomoPayment(
        partnerCode = partnerCode,
        orderId = orderId,
        requestId = requestId,
        amount = amount,
        orderInfo = orderInfo,
        orderType = orderType,
        transId = transId,
        payType = payType,
        signature = signature
    )
    db.session.add(new_mompayment)
    db.session.commit()
    db.session.close()
