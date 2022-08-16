from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import JsonResponse,HttpResponse
from UserData.models import Family,Booking,report,userAddress,Prescriptions
from django.conf import settings
from superuser.forms import GenForm
import mimetypes
from django.db.models import Q

def download_file(filepath):
    # Define Django project base directory
    # Define text file name
    filename = 'report'+ filepath[filepath.rfind('.'):]
    # Define the full file path
    print(filepath)
    filepath = settings.MEDIA_ROOT / filepath
    # Open the file for reading content
    print(filepath)

    path = open(filepath, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    # Return the response value
    return response


def dashboard(request):
    res={}
    res['bodyclass'] = "dashboard"
    res['pagetitle'] = "Dashboard"
    return render(request,'UserData/user/dashboard.html',res)
def subscription(request):
    res = {}
    res['pagetitle'] = "Subscriptions"
    res['bodyclass'] = "faimly-friendwraper"
    return render(request,'UserData/user/subscription.html',res)

from operator import itemgetter
def profile(request):
    res = {}
    res['pagetitle'] = "Profile"
    if request.method == "POST":
        if request.GET.get('profile') == "update":
            profile= request.FILES['my_pics']
            request.user.profile = profile
            request.user.save()
            messages.success(request,"Profile picture updated")
            if request.GET.get('next') is not None:
                return redirect(request.GET.get('next'))
            return redirect(request.path)
        name,gender,dob =  itemgetter('name','gender','dob')(request.POST)
        name = name.strip().split(' ')
        if len(name)>=1:request.user.first_name = name[0]
        if len(name)==2:request.user.last_name = name[1]
        request.user.gender = gender
        request.user.dob = dob
        request.user.save()
        messages.success(request,"Profile updated")
        if request.GET.get('next') is not None:
            return redirect(request.GET.get('next'))
        return redirect(request.path)
    res['bodyclass'] = "faimly-friendwraper"
    return render(request,'UserData/user/profile.html',res)
def booking(request):
    res = {}
    res['pagetitle'] = "Bookings"
    res['bodyclass'] = "faimly-friendwraper"
    res['Bookings'] = Booking.objects.filter(Q(user=request.user.id) , Q(status='success')|Q(status='cod')).order_by("-id")
    return render(request,'UserData/user/booking.html',res)
def Report(request,slug=None):
    if slug is not None:
        repofile = report.objects.get(id=slug).report
        return download_file(str(repofile))
    res = {}
    res['pagetitle'] = "Reports"
    res['reports'] = report.objects.filter(booking__user=request.user)
    res['bodyclass'] = "faimly-friendwraper"
    return render(request,'UserData/user/report.html',res)
def family(request):
    res = {}
    res['pagetitle'] = "My Family"
    if request.method=="POST":
        id = request.POST.get('customer_id')
        if id is not None and len(id) != 0:
            instance = Family.objects.get(id=id)
        else:
            instance =None
        form = GenForm(Family)(request.POST,instance=instance)
        if form.is_valid():
            form.save()
            if instance is None:
                messages.success(request,'Member added successfully')
            else:
                messages.success(request,'Member updated successfully')
        else:
            for data in form.errors:
                messages.error(request,str(data))
        if request.GET.get('next') is not None:
            return redirect(request.GET.get('next'))
        
        return redirect(request.path)
    res['bodyclass'] = "faimly-friendwraper"
    return render(request,'UserData/user/family.html',res)
from django.core.serializers import serialize


def getMember(request):
    id = request.GET.get('memberid')
    data = serialize('python',Family.objects.filter(id=id))
    return JsonResponse(data[0]['fields'],safe=False)
def deleteMember(request,id):
    try:
        Family.objects.get(id=id,user=request.user).delete()
        messages.success(request,"Family member deleted")
    except Exception as e:
        print(e)
        messages.error(request,"Not allowed Invalid request")
    return redirect('family')
def getaddress(request):
    id = request.GET.get('addressid')
    data = serialize('python',userAddress.objects.filter(id=id))
    return JsonResponse(data[0]['fields'],safe=False)
def deleteaddress(request,id):
    try:
        userAddress.objects.get(id=id,user=request.user).delete()
        messages.success(request,   "Address deleted")
    except:
        messages.error(request, "Not allowed Invalid request")
    if request.GET.get('next') is not None:
        return redirect(request.GET.get('next'))
    return redirect("address")
def address(request):
    if request.method == "POST":
        id = request.POST.get('id')
        if id is not None and len(id) != 0:
            instance = userAddress.objects.get(id=id)
        else:
            instance =None
        form = GenForm(userAddress)(request.POST,instance=instance)
        print(request.POST)
        if form.is_valid():
            form.save()
            if instance is None:
                messages.success(request,'Address added successfully')
            else:
                messages.success(request,'Address updated successfully')
            if request.GET.get('next') is not None:
                return redirect(request.GET.get('next'))
            return redirect(request.path)
        else:
            for key,value in form.errors.as_data().items():
                msg = ""
                for data in value:
                    for v in data:
                        msg+=str(v)+"<br>"
                msg = msg[:msg.rfind('<br>')]
                messages.error(request,f"{key}: {msg}")
            
    res = {}
    res['bodyclass'] = "faimly-friendwraper"
    res['address'] = userAddress.objects.filter(user=request.user.id)
    res['pagetitle'] = "Address"
    return render(request,'UserData/user/address.html',res)


def uploadprescription(request):
    res= {}
    res['pagetitle'] = "Upload Prescription"
    res['bodyclass'] = 'upload-page'
    if request.method=="POST":
        print(request.POST,request.FILES)
        dictdata = {'user':request.user}
        count = 0
        for data in request.FILES.getlist('files[]'):
            count+=1
            if count <=3:
                dictdata[f'image{count}'] = data
        presimg = Prescriptions(**dictdata)
        presimg.save()
        messages.success(request,'Your Prescription uploaded successfully we will get back to you soon')
        return JsonResponse({"uploaded":True,'status':True,'url':request.path})
    return render(request,'UserData/user/uploadprescription.html',res)

   