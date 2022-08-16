from django.shortcuts import redirect, render
from django.contrib import messages
from UserData.models import report,Booking
from UserData.Signals import sendmail
from threading import Thread
from superuser.custumfunction import getobjecturl
def sendBulkMail(request):
    maildata = request.POST.get("HandleSendReportinput").split(',')
    count = 0
    usernames = ''
    for data in maildata:
        count += 1
        d = report.objects.get(id=data)
        email = d.booking.user.email
        Thread(target=sendmail, args=(d,email)).start()
        if count < 5:
            usernames += str(getobjecturl(d.booking.user)) + " , "
    messages.success(request,"mail sent to" + usernames + "   .....")
    return redirect(request.GET.get('next'))
def bulkreportupload(request):
    res={}
    res['title'] = "Bulk Report Upload"
    res['dashboardheading'] = "Bulk Report Upload"
    updated = 0
    ignore = 0
    create = 0
    if request.method=="POST":
        for data in request.FILES.getlist('reports'):
            filename=(data.name[:data.name.rfind(".")]).strip()
            bookingob = Booking.objects.filter(Booking_id=filename)
            if bookingob.exists():
                reportob,created = report.objects.get_or_create(booking=bookingob[0],)
                if created:
                    create+=1
                else:
                    updated +=1
                reportob.report=data
                reportob.save()
            else:
                ignore +=1
        messages.success(request,f"Total {len(request.FILES.getlist('reports'))} reports uploaded, {updated} reports are updated and {ignore} files has invalid name and {create} new records are created")
        return redirect(request.GET.get('next'))
    return render(request,'superuser/bulkreportupload.html',res)