from threading import Thread

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import package, tempbooking,Subcategory,test,category, coupon , profile
from UserData.models import cart,Family,Booking, userAddress
from datetime import datetime
from itertools import chain
from django.core.mail import EmailMessage
from paymentintigration.views import getPaytmParam, verifyPaymentRequest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from superuser.views import getEmailBackend
from superuser.forms import GenForm
# from django.contrib.postgres.aggregates import ArrayAgg
# Create your views here.
def packagedetails(request,slug):
    res = {}
    res['package'] = package.objects.get(slug=slug)
    res['pagetitle'] = res['package'].Package_name
    qry = [data['id'] for data in res['package'].package_category.all().values('id')]
    res['related'] = package.objects.filter(package_category__in=qry,Publish="1",final_cost__gt=0).exclude(slug=slug).distinct()
    print(res['related'])
    # print(res['package'].package_category.all().values_list('id'))
    totaltest = 0
    for data in res['package'].Porfile_collection.all():
        totaltest += data.Select_Test_id.all().count()
    res['totaltest'] = totaltest
    return render(request,'package/packageDetails.html',res)
def testdetails(request,slug):
    res = {}
    res['package'] = test.objects.get(slug=slug)
    res['pagetitle'] = res['package'].test_name 
    qry = [data['id'] for data in res['package'].test_category.all().values('id')]
    res['related'] = test.objects.filter(test_category__in=qry,Publish="1",final_cost__gt=0).exclude(slug=slug).distinct()
    totaltest = 0
    res['totaltest'] = totaltest
    return render(request,'package/testDetails.html',res)

def getbycategory(request,slug='slug'):
    res= {}
    res['bodyclass'] = "risk-page"
    return render(request,'package/listpackage.html',res) 
def getbysubcategory(request,subcategory=None,catename=None,type='package'):
    res= {}
    if subcategory is not None:
        slug = subcategory
        res['category'] = Subcategory.objects.get(slug=slug)
    if catename is not None:
        slug = catename
        res['category'] = category.objects.get(slug=slug)
    res['pagetitle'] = res['category'].name
    res['type'] = type
    res['bodyclass'] = "risk-page"
    res['subcate'] = subcategory
    page = request.GET.get('page', 1)
    if type=='test':
        # print('working')
        if subcategory is not None:
            res['packages'] = test.objects.filter(test_category__slug=slug,Publish='1',final_cost__gt=0)
        else:
            res['packages'] = test.objects.filter(test_category__category__slug=slug,Publish='1',final_cost__gt=0)
    else:
        if subcategory is not None:
            res['packages'] = package.objects.filter(package_category__slug=slug,Publish='1')
        else:
            res['packages'] = package.objects.filter(package_category__category__slug=slug,Publish='1')
    res['packages'] = res['packages'].distinct()
    res['packages'] =Paginator(res['packages'], 12)
    try:
        res['packages'] = res['packages'].page(page)
    except PageNotAnInteger:
        res['packages'] = res['packages'].page(1)
    except EmptyPage:
        res['packages'] = res['packages'].page(res['packages'].num_pages)
    return render(request,'package/listpackage.html',res) 
    

@login_required(login_url='userlogin')
def booknow(request,slug,type):
    res= {}
    res['pagetitle'] = "Book-Now"
    if len(request.user.first_name.replace(' ','')) == 0:
        path = reverse("registration")+ "?next="+request.get_full_path()
        return redirect(path)
    res['member'] = request.user.Family.all()
    if type=='package':
        buypackage = package.objects.get(slug=slug)
        totaltest = 0
        for data in buypackage.Porfile_collection.all():
            totaltest += data.Select_Test_id.all().count()
        res['totaltest'] = totaltest
        res['totleprize'] = float(buypackage.final_cost)*(res['member'].count()+1)
        res['totalsaving'] =(float(buypackage.Package_price) -float(buypackage.final_cost))*(res['member'].count()+1)
        buytest = None
    else:
        buypackage = None
        buytest = test.objects.get(slug=slug)
        res['totleprize'] = float(buytest.final_cost)*(res['member'].count()+1)
        res['totalsaving'] =(float(buytest.test_price) -float(buytest.final_cost))*(res['member'].count()+1)
    res['type'] = type
    res['package'] = buypackage
    res['test'] =buytest
    res['address'] = userAddress.objects.filter(user=request.user.id)
    cart.objects.update_or_create(user=request.user,package=buypackage,test=buytest)
    res['family'] = Family.objects.filter(user= request.user)
    if request.method=="POST":
        print(request.POST)
        date = request.POST['colletiondate']
        time = request.POST['colletiontime']
        datime = datetime.strptime(date+" "+time,'%Y-%m-%d %H:%M')
        if res['address'].exists():
            try:
                address = request.POST['address']
            except Exception:
                messages.error(request,"Please add Address first")
                return redirect(request.path)
        else:
            form = GenForm(userAddress)(request.POST,instance=None)
            if form.is_valid():
                address = form.save()
                address = address.id
        coupencode = request.POST['coupencode']
        address = userAddress.objects.filter(id=address)[0]
        try:
            paymode = request.POST['payoption']
        except Exception:
            messages.error(request,"Please Select Payment option")
            return redirect(request.path)
        forself = True if request.POST.get('self') == 'on' else False
        familymember = []
        for data in request.POST:
            val = request.POST[data]
            if 'member' in data and val == "on":
                familymember.append(data)
        ammount = 0.0
        tran = tempbooking(user=request.user,ammount=0)
        tran.save()
        for data in familymember:
            mem = Family.objects.get(id=data.replace('member',''))
            newbooking = Booking(user=request.user,type=type,package=buypackage,test=buytest,collectiontime=datime,bookingfor=data,member=mem,address=address)
            newbooking.save()
            if buypackage is not None:
                ammount+=float(buypackage.final_cost)
            else:
                ammount+=float(buytest.final_cost)
            tran.bookingid.add(newbooking)
        if forself:
            newbooking = Booking(user=request.user,type=type,package=buypackage,test=buytest,collectiontime=datime,bookingfor='self',address=address)
            newbooking.save()
            if buypackage is not None:
                ammount+=float(buypackage.final_cost)
            else:
                ammount+=float(buytest.final_cost)
            tran.bookingid.add(newbooking)
        tran.ammount = ammount
        tran.save()
        validate = validateCoupen(request,coupencode,ammount)
        print(validate)
        if validate['success']:
            tran.coupon = validate['code']
            discount = validate['discount']
            amm = tran.ammount
            if '%' in discount:
                dis = float(discount.replace('%',''))
                tran.ammount = amm -((amm*dis)/100)
            else:
                tran.ammount = amm - float(discount)
        tran.save()
        print(tran.ammount)
        if int(tran.ammount)<1:
            tempbook = tempbooking.objects.get(tempbookingid = tran.tempbookingid)
            tempbook.status = 'success'
            tempbook.save()
            validateCoupen(request,coupencode,ammount,use=True)
            for data in tempbook.bookingid.all():
                data.status="success"
                data.save()
                email = data.user.email
            Thread(target=sendBookingNortification, args=(tempbook.tempbookingid,email)).start()
            return render(request,'package/paymentstatus.html',{'response': {'RESPCODE':'01','ORDERID':tempbook.tempbookingid}})
        if paymode == "paytm":
            return getPaytmParam(request,tran.tempbookingid,tran.ammount,request.user.phone,'handlePaytm',"INR")
        elif paymode == "cod":
            tempbook = tempbooking.objects.get(tempbookingid = tran.tempbookingid)
            tempbook.status = 'success'
            tempbook.save()
            validateCoupen(request,coupencode,ammount,use=True)
            for data in tempbook.bookingid.all():
                data.status="cod"
                data.save()
                email = data.user.email
            Thread(target=sendBookingNortification, args=(tempbook.tempbookingid,email)).start()
            return render(request,'package/paymentstatus.html',{'response': {'RESPCODE':'01','ORDERID':tempbook.tempbookingid}})
        return redirect(request.path)
    return render(request,'package/booknow.html',res)
def sendBookingNortification(bookinid,emailadress):
    backend , config = getEmailBackend()
    email = EmailMessage("Sequal | Order",f'Your Order booked successfully your order id is {bookinid}',config.email,[emailadress],connection=backend)
    email.send()
@csrf_exempt
def handlepaytm(request):
    print(request.POST)
    verify,response_dict = verifyPaymentRequest(request)
    if verify:
        if response_dict['RESPCODE'] == '01':
            tempbook = tempbooking.objects.get(tempbookingid = response_dict['ORDERID'])
            response_dict['booking'] = tempbook
            tempbook.status = 'success'
            tempbook.save()
            validateCoupen(request,tempbooking.coupon,response_dict['TXNAMOUNT'],use=True)
            for bob in tempbook.bookingid.all():
                bob.status="success"
                bob.save()
                email = bob.user.email
            Thread(target=sendBookingNortification, args=(tempbook.tempbookingid,email)).start()
            response_dict['couse'] = float(response_dict['TXNAMOUNT'])
        else:
            try:
                tempbook = tempbooking.objects.get(tempbookingid = response_dict['ORDERID'])
                for data in tempbook.bookingid.all():
                    data.delete()
            except Exception as e:
                pass
    else:
            print("order unsuccessful because",response_dict['RESPMSG'])
    return render(request,'package/paymentstatus.html',{'response': response_dict,'pagetitle':'Payment Status'})

def Test(request):
    numbers_list = range(1, 1000)
    page = request.GET.get('page', 1)
    paginator = Paginator(numbers_list, 20)
    try:
        numbers = paginator.page(page)
    except PageNotAnInteger:
        numbers = paginator.page(1)
    except EmptyPage:
        numbers = paginator.page(paginator.num_pages)
    return render(request, 'package/test1.html', {'numbers': numbers})
def searchinModel(modelname,qry):
    if qry is not None:
        print('if working')
        from django.db.models import  Q
        from django.db.models import CharField
        fields = [f for f in modelname._meta.fields if isinstance(f, CharField)]
        queries = [Q(**{f.name+'__icontains': qry}) for f in fields]
        qs = Q()
        for query in queries:
            qs = qs | query
        print(qs)
        res = modelname.objects.filter(qs)
        print(res)
        return res
    return []
def search(request):
    res={}
    res['bodyclass'] = "risk-page"
    qry = request.GET.get('q')
    res['pagetitle'] = qry
    page = request.GET.get('page',None)
    if qry is not None:
        # searchresult = chain(searchinModel(package,qry),searchinModel(test,qry))
        # searchresult = []
        # for data in searchinModel(test,qry):
        #     searchresult.append(data)
        # for data in searchinModel(package,qry):
        #     searchresult.append(data)
        profiles = searchinModel(profile,qry)
        print(profiles)
        result = set()
        for data in profiles:
            result = result.union(set(data.package.all())) 
        filtertest = searchinModel(test,qry)
        for data in filtertest:
            result = result.union(set(package.objects.filter(Porfile_collection__Select_Test_id=data.id))) 
        print(result)
        result = result.union(set(searchinModel(package,qry)))
        searchresult = list(chain(filtertest.filter(final_cost__gt=0),result))
        print(searchresult)
        paginator = Paginator(searchresult, 12)
        try:
            result = paginator.page(page)
        except PageNotAnInteger:
            result = paginator.page(1)
        except EmptyPage:   
            result = paginator.page(paginator.num_pages)
        res['result'] = result
    return render(request,'package/search.html',res)

def validateCoupen(request,code,ordervalue,use=False):
    res= {}
    res['code'] = code
    res['success'] = False
    if code is None or len(code)==0:
        res['message'] = "please add coupen code"
        res
    couponob = coupon.objects.filter(Generate_coupon=code,active='1')
    if not couponob.exists():
        res['message'] = "Please Enter a valid coupen code"
        return res
    couponob = couponob[0]
    if use:
        couponob.used = couponob.used+1
        couponob.save()
        return res
    if couponob.remaining > 0:
        res['message'] = "This Coupen is expired"
        return res
    if  datetime.now().date() > couponob.Coupon_expire_date:
        res['message'] = "This Coupen is expired"
        return res
    if tempbooking.objects.filter(user=request.user.id,coupon=code,status='success').exists():
        res['message'] = "You Already Used This Coupen"
        return res
    if couponob.minimum_order_value > float(ordervalue):
        res['message'] = f'minimum ₹{couponob.minimum_order_value} ordervalue is required'
        return res
    res['success'] = True
    res['message']=couponob.message
    res['discount'] = couponob.discount
    
    return res
@login_required(login_url='userlogin')
def getCoupenDetails(request):
    code = request.GET.get('coupen')
    ordervalue = request.GET.get('ordervalue')
    res= validateCoupen(request,code,ordervalue)
    return JsonResponse(res)
    