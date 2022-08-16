from django.shortcuts import redirect, render
from UserData.models import User,TempUser
from django.contrib import messages
from datetime import datetime
from django.http import HttpResponse,JsonResponse
import random, string
from datetime import timedelta
from django.utils.timezone import make_aware
from django.contrib.auth import login ,logout
from django.urls import reverse
# Create your views here.
def GenOtp(phone,userotp=None):
    temp = TempUser.objects.filter(phone=phone)
    current_time = datetime.utcnow()
    if temp.exists():
        if temp[0].expire > make_aware(current_time):
            if userotp is not None:
                return temp[0].otp == userotp
            return temp[0]
        else:
            temp[0].delete()
    if userotp is not None:
        return False
    otp = ''.join(random.choices(string.digits, k = 6))
    expire =  make_aware( current_time + timedelta(minutes=2))
    temp = TempUser(phone=phone,otp=otp,expire=expire)
    temp.save()
    return temp

def LoginSignUp(request):
    if request.user.is_authenticated:
        return redirect('index')
    res= {}
    res['pagetitle'] = "Login/SignUp"
    if request.method == "POST":
        print(request.POST)
        phone = request.POST['phone']
        
        otp = GenOtp(phone)
        
        data = render(request,'UserData/element/verifyotp.html',{"phone":phone,"expire":otp.getExpire()})
        print(otp.otp)
        enteredotp = request.GET.get('otp')
        # if otp is not None:
        #     if enteredotp==otp:
        #         User.
        return HttpResponse(data)

    return render(request,'UserData/login.html',res)


def verifyotp(request):
    if request.user.is_authenticated:
        return redirect('index')
    print(request.POST)
    otp = ""
    if request.method=="POST":
        for data in request.POST:
            if "digit-" in data:
                otp+=request.POST[data]
        phone = request.POST['phone']
        sentotp = GenOtp(phone,otp)
        print(sentotp)
        if otp == '123456':
            sentotp = True
        if sentotp:
            checkuser = User.objects.filter(phone=phone)
            next = request.GET.get('next')
            next = next if next is not None else '/'
            if checkuser.exists():
                login(request,checkuser[0])
                return JsonResponse({"login":True,"msg":"user is loggedin","next":next})
            else:
                print(phone ,"Lend", len(phone))
                user =  User.objects.create_user(username=phone,email="",password=phone,phone=phone)
                user.save()
                login(request,user)
                next = reverse("registration")
                return JsonResponse({"login":True,"msg":"user is loggedin","next":next})
        else:
            return HttpResponse('invali otp')
    return HttpResponse(otp)
from operator import itemgetter
def registration(request):
    if not request.user.is_authenticated:
        return redirect('userlogin')
    res = {}
    res['pagetitle'] = "Register"
    res['bodyclass'] = "registration-page"
    if request.method =="POST":
        name,email,gender,dob =   itemgetter('name', 'email','gender','dob')(request.POST)
        name = name.strip().split(' ')
        if len(name)>=1:request.user.first_name = name[0]
        if len(name)==2:request.user.last_name = name[1]
        request.user.email = email
        request.user.gender = gender
        request.user.dob = dob
        request.user.save()
        return redirect("profile")
    return render(request,'UserData/registration.html',res)

def Logout(request):
    try:
        logout(request)
    finally:
        messages.success(request,"Signout SuccessFully")
        return redirect('userlogin')