from django.apps import config
from django.shortcuts import render
from .models import PaytmConfig, rozpayConfig , paypalConfig,PaytmTransaction
from .paytm import Checksum
from django.conf import settings
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.ipn.models import PayPalIPN
import razorpay
# Create your views here.
from django.urls import reverse
def getPaytmParam(request,orderid:str,ammount:float,cust_id:str,callbackpathname:str,currency:str):
    config = PaytmConfig.objects.get(activate=True)
    callback = "https://" if request.is_secure() else "http://"
    callback += request.get_host() + reverse(callbackpathname)
    print(callback)
    param_dict = {
            'MID':config.MID,
            'ORDER_ID': orderid,
            'TXN_AMOUNT':str(ammount),
            'CUST_ID': cust_id,
            'INDUSTRY_TYPE_ID':'Retail',
            'WEBSITE':config.get_WEBSITE_display(),
            'CHANNEL_ID':'WEB',
            'CALLBACK_URL':callback,}
    print(param_dict)
    param_dict['CHECKSUMHASH']=Checksum.generate_checksum(param_dict,config.MERCHANT_KEY)  
    param_dict['CURRENCY'] 	= currency
    print("dfsdf")
    renderhtml = render(request,'paymentintigration/paytm.html', {'param_dict':param_dict,'paytmposturl':config.PostUrl })
    return renderhtml


def verifyPaymentRequest(request):
    config = PaytmConfig.objects.get(activate=True)
    form = request.POST
    print(request.POST)
    response_dict= {}
    for i in form.keys():
        response_dict[i]=form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]
    print(response_dict)
    try:
        PaytmTransaction(**response_dict).save()
    except Exception as e:
        print("+++++++++++++++++=exception in push trastion",e)
    verify = Checksum.verify_checksum(response_dict,config.MERCHANT_KEY,checksum)
    return verify,response_dict



def PaypalParam(request,order_id,order_name,ammount,currency):
    host = "https://" if request.is_secure() else "http://"
    host += request.get_host()
    config = paypalConfig.objects.get(activate=True)
    settings.PAYPAL_TEST = config.test
    paypal_dict = {
        'business': config.RECEIVER_EMAIL,
        'amount': ammount,
        'item_name': order_name,
        'invoice': order_id,
        'currency_code': 'USD',
        'notify_url': '{}{}'.format(host,
                                           reverse('paypal-ipn')),
        'return_url': '{}{}'.format(host,
                                           reverse('payment_done')),
        'cancel_return': '{}{}'.format(host,
                                              reverse('payment_cancelled')),
    }
    form = PayPalPaymentsForm(initial=paypal_dict)
    return paypal_dict,form
def verifyPayPalPayment(orderid):
    return PayPalIPN.objects.get(invoice=orderid).__dict__

def getRozorpayClient():
    config = rozpayConfig.objects.get(activate=True)
    return razorpay.Client(
    auth=(config.RAZOR_KEY_ID, config.RAZOR_KEY_SECRET)),config