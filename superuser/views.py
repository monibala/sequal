# from django.http import request
# from django.http.response import HttpResponse
from django.contrib import messages
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from .custumfunction import getobjecturl
from superuser.templatetags.custumfilter import sidebardata
from .dashboardsettings import appmodels , appslist , getObjectbyAppModelName , getmodelbyappname
from django.core import serializers
from .forms import GenForm
from django.contrib.auth import authenticate, login, logout
from superuser.dashboardsettings import exclude as excludeapps
from django.db.models.fields import related
from superuser.dashboardsettings import hiddenFields,disablefield
from .models import emailSetup
import csv
from django.core.mail.backends.smtp import EmailBackend

# from django.apps import apps
# from onlineshop.models import *
# from django.contrib import messages
# from .forms import ProductForm,aboutForm,about,GenForm
# Create your views here.
#add all app names you want to oprate in admin
allapps = appslist
def get_all_fields(self):
    """Returns a list of all field names on the instance."""
    fields = []
    for f in self._meta.fields:

        fname = f.name        
        # resolve picklists/choices, with get_xyz_display() function
        get_choice = 'get_'+fname+'_display'
        if hasattr(self, get_choice):
            value = getattr(self, get_choice)()
        else:
            try:
                value = getattr(self, fname)
            except AttributeError:
                value = None

        # only display fields with values and skip some fields entirely
        if f.editable and value and f.name not in ('id', 'status', 'workshop', 'user', 'complete') :

            fields.append(
              {
               'label':f.verbose_name, 
               'name':f.name, 
               'value':value,
              }
            )
    return fields
def index(request):
    res = {}
    res['title'] = 'Dashboard'
    res['dashboardheading'] = 'Dashboard'
    # for data in res['modelslist']:
    #     print(res['modelslist'][data])
    #     break
    # for app in allapps:
    #     res.append({app:apps.all_models[app]})
    return render(request,'superuser/index.html',res)

def showmodels(request,appname):
    res = {}
    res['modelname'] ="Home"
    res['appname'] =appname
    res['title'] =appname
    res['models'] = getmodelbyappname(appname)
    return render(request,'superuser/listmodels.html',res)

def showObject(request,appname,modelname):
    res = {}
    mymodel = getObjectbyAppModelName(appname,modelname)
    res['modeldata'] = mymodel.objects.all()
    if mymodel._meta.object_name=='User' and mymodel._meta.app_label=="UserData":
    # if mymodel.__module__ == "UserData.models":
        res['fields'] = [['id','type'],['first_name','type'],['last_name','type'],['phone','type'],['email','type'],['last_login','type'],['username','type'],['dob','type'],['profile','type'],['gender','type'],['date_joined','type']]
    else:
        res['fields'] = [[f.name,str(type(f))] for f in mymodel._meta.fields]
    # res['fields'] = [f.name for f in mymodel._meta.get_fields()]
    res['modeldata'] = mymodel.objects.all()
    res['appname'] =appname
    res['modelname'] =modelname
    res['title'] =modelname
    try:
        res['oprations'] = mymodel().BulkOprationButton()
    except:
        pass
    return render(request , 'superuser/modeldatatable.html' ,res)
from io import BytesIO as IO
import pandas as pd
def ExportData(request,appname,modelname,type):
    mymodel = getObjectbyAppModelName(appname,modelname)
    modelob = mymodel.objects.all() 
    fields = [f.name for f in mymodel._meta.fields]
    values = [fields]
    for data in modelob:
        values.append([ str(getattr(data,name)) for name in fields ])
        # writer.writerow([ getattr(data,name) for name in fields ])
    if type=='fexcel':
        response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{appname}-{modelname}.xls"'
        writer = csv.writer(response)
        writer.writerow(fields)
        for data in values:
            writer.writerow(data)
        return response
    if type=='excel':
        excel_file = IO()
        df_output = pd.DataFrame(values)
        xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
        df_output.to_excel(xlwriter, 'sheetname',index=False)
        xlwriter.save()
        xlwriter.close()
        excel_file.seek(0)

        # set the mime type so that the browser knows what to do with the file
        response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        # set the file name in the Content-Disposition header
        response['Content-Disposition'] = f'attachment; filename="{appname}-{modelname}.xlsx'
        return response
from .dashboardsettings import showRelatedOnEditPage
def editmodel(request,appname=None,modelname=None,objectid=None,opration=None):
    res = {}
    mymodel = getObjectbyAppModelName(appname,modelname)
    hfield = ['slug']
    hfield = cheackField(hfield,hiddenFields,appname=appname,modelname=modelname)
    Dfield = cheackField(avFields=disablefield,appname=appname,modelname=modelname)
    form = GenForm(mymodel,hfield,Dfield)
    res['appname'] =appname
    res['modelname'] =modelname
    if objectid is not None and objectid != "newmodel":
        if not (objectid=='multidelete'):
            singledata = mymodel.objects.get(pk=objectid)
        else:
            singledata = objectid
    if opration == 'add':
        res['form'] = form()
        res['title'] = "add " + modelname
        if request.method == "POST":
            res['form'] = form(request.POST,request.FILES)
            if res['form'].is_valid():
                res['form'].save()
                messages.success(request,str(getobjecturl(res['form'].instance)) + " is saved successfully")
                return redirect(request.get_full_path())
            messages.error(request,str(getobjecturl(res['form'].instance)) + " data is invalid Check your form")
    elif opration == 'edit':
        res['title'] = "edit " + modelname
        if f"{appname}.{modelname}" in showRelatedOnEditPage:
            res['showrelated'] = True
        res['form'] = form(instance=singledata)
        res['relateddata'] = type(singledata)._meta.related_objects
        res['appname'] = appname
        res['modelname'] = modelname
        res['objectid'] = objectid
        if request.method == "POST":
            res['form'] = form(request.POST,request.FILES,instance=singledata)
            if res['form'].is_valid():
                res['form'].save()
                messages.success(request,str(getobjecturl(res['form'].instance))  + " is saved successfully")
                if request.GET.get('next') is not None:
                    return redirect(request.GET.get('next'))
                return redirect(request.get_full_path())
            messages.error(request,str(res['form'].instance) + " data is invalid Check your form")
            
    elif opration == 'delete':
        confirm = request.POST.get('confirm')
        return alertdelete(request,singledata,confirm,appname,modelname)
    return render(request,'superuser/editmodel.html',res)

def cheackField(field=[],avFields=[],appname='', modelname=''):
    nfield = field
    for data in avFields:
        data = data.split('.')
        if appname==data[0] and modelname==data[1]:
            nfield.append(data[2])
    return field

def relatedmodel(request,appname=None,modelname=None,objectid=None,relatedfield=None):
    res= {}
    res['title'] = modelname+" | " + relatedfield
    mymodel = getObjectbyAppModelName(appname,modelname)
    singledata = mymodel.objects.get(pk=objectid)
    res['appname'] = appname
    res['modelname'] = modelname
    res['objectid'] = objectid
    res['currentmodel'] = singledata
    try:
        relatedfieldobject = getattr(singledata,relatedfield)
    except getattr(mymodel._meta.model,relatedfield).RelatedObjectDoesNotExist:
        result =  (list(filter(lambda x : (x.related_name==relatedfield), mymodel._meta.related_objects)))[0]
        relatedmodel =   result.related_model._meta.verbose_name
        relappname = result.related_model._meta.app_label
        res['title'] = "edit " + modelname
        if f"{appname}.{modelname}" in showRelatedOnEditPage:
            res['showrelated'] = True
        form = GenForm(result.related_model,listHiddenfield=[result.field.name])
        inidic = {result.field.name:singledata.id}
        print(inidic)
        res['form'] = form(initial=inidic)
        if request.method=='POST':
            res['form'] = form(request.POST,request.FILES)
            if res['form'].is_valid():
                res['form'].save()
                messages.success(request,str(getobjecturl(res['form'].instance)) + " is saved successfully")
                if request.GET.get('next') is not None:
                    return redirect(request.GET.get('next'))
                return redirect(request.get_full_path())
            messages.error(request,str(getobjecturl(res['form'].instance)) + " data is invalid Check your form")
        return render(request,'superuser/editmodel.html',res)
        # return redirect('editdatamodel',appname=relappname,modelname=relatedmodel,opration='add',objectid='newmodel')
    try:
        res['availbledata'] = relatedfieldobject.all()
    except:
        result =  (list(filter(lambda x : (x.related_name==relatedfield), mymodel._meta.related_objects)))[0]
        relatedmodel =   result.related_model._meta.verbose_name
        relappname = result.related_model._meta.app_label
        return redirect('editdatamodel',appname=relappname,modelname=relatedmodel,opration='edit',objectid=relatedfieldobject.id)

    relmodel = relatedfieldobject.model
    relatedfieldobjectFieldname = relatedfieldobject.field.name
    hfield = [relatedfieldobjectFieldname,'slug']
    hfield = cheackField(hfield,hiddenFields,appname=appname,modelname=modelname)
    Dfield = cheackField(avFields=disablefield,appname=appname,modelname=modelname)
    form = GenForm(relmodel,hfield,Dfield)
    res['currentmodelname'] = relatedfieldobject.model._meta.verbose_name
    res['currentappname'] = relatedfieldobject.model._meta.app_label
    res['currentmodelfieldname'] = relatedfieldobject.model._meta.model_name
    if request.method == "POST":
        res['form'] = form(request.POST,request.FILES)
        if res['form'].is_valid():
            res['form'].save()
            messages.success(request,"new "+ res['currentmodelname'] + "is added in "+modelname +" Successfully"  )
            return redirect(request.get_full_path())
        else:
            messages.error(request,'Invalid data please cheack your form')
            return render(request,'superuser/relatedmodel.html',res)
    if relmodel is not None:
        res['fields'] = [[f.name,str(type(f))] for f in relmodel._meta.fields]
    
    res['currentmodelobjectid'] = singledata.pk
    res['form'] = form(initial={relatedfieldobjectFieldname: singledata.pk})
    return render(request,'superuser/relatedmodel.html',res)


from django.core.exceptions import ValidationError
from django.contrib.admin.utils import NestedObjects
def alertdelete(request,singledata,confirm="None",appname ='', modelname=''):
    print(request.POST)
    print(singledata)
    if singledata=="multidelete":
        mymodel = getObjectbyAppModelName(appname,modelname)
        singledata = [mymodel.objects.get(id=data) for data in request.POST.get('delete').split(',')]
        print(singledata)
    else:
        singledata = [singledata]
    if confirm == "delete":
        name = ""
        for data in singledata:
            name += str(data)+ " ,"
            try:
                data.delete()
            except ValidationError as e:
                messages.error(request,e.message)
                return redirect('showdatamodel',appname=appname,modelname=modelname )
        messages.success(request,name + " is deleted successfully")
        return redirect('showdatamodel',appname=appname,modelname=modelname )
    res = {}
    res['title'] = "delete " + modelname
    using = 'default'
    nested_object = NestedObjects(using)
    nested_object.collect(singledata)
    res['deletedata'] = nested_object.nested()
    res['appname'] = appname
    res['modelname'] = modelname
    res['currentmodel'] = singledata
    return render(request , 'superuser/confirmdelete.html',res)
def Logout(request):
    try:
        logout(request)
    except Exception as e:
        return redirect('index')
    return redirect('index')

def logindashboard(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('dashboardindex')
    if request.method=="POST":
        print(request.POST,"this is working")
        username = request.POST.get('username')
        password = request.POST.get('password')
        USER = authenticate(request,username=username, password=password)
        if USER is not None:
            login(request, USER)
            if request.user.is_superuser:
                return JsonResponse({'status':'ok','msg':'Login Success','next':request.GET.get('next'),'type':'success'})
            return JsonResponse({"status":'invaliduser','msg':'invalid user','type':'danger'})
        return JsonResponse({"status":'invaliduser','msg':'Invalid Credentials','type':'danger'})
    return render(request,'superuser/logindashboard.html')



def getEmailBackend():
    config = emailSetup.objects.get(activate=True)
    backend = EmailBackend(host=config.host, port=config.port, username=config.email, 
                       password=config.password, use_tls=config.tsl,use_ssl=config.ssl )
    return backend , config







# def allproducts(request):
#     prods = Product.objects.all()
#     return render(request,'superuser/products.html',{'prods':prods,'title':"View Product"})
# def editproduct(request,id=None,task=None):
#     res = {}
#     if task == 'add':
#         res['form'] = ProductForm()
#         instan = None
#     if task == 'edit':
#         instan = Product.objects.get(id=id)
#         res['form'] = ProductForm(instance=instan)
#     if request.method == "POST":
#         res['form'] = ProductForm(request.POST,request.FILES,instance=instan)
#         if res['form'].is_valid():
#             res['form'].save()
#             messages.success(request,"Prouduct is added successfully :)")
#         return render(request,'superuser/addprod.html',res)
#     if task == 'del':
#         return delproduct(request,id)
#     return render(request,'superuser/addprod.html',res)


# def delproduct(request,id=None):
#     if id is not None:
#         Product.objects.get(id=id).delete()
#         return redirect('allproducts')

# def addspecs(request,id,update=False,remove = False):
#     prod = Product.objects.get(id=id)
#     specsob = specs.objects.filter(Product=prod.id)
#     if request.method == "POST":
#         title = request.POST['title']
#         oldtitle = request.POST.get('oldtitle')
#         key = request.POST.getlist('key')
#         value = request.POST.getlist('value')
#         data = {}
#         data[title] = [[key[i],value[i]] for i in range(0,len(key))]
#         if specsob.exists():                
#             specsobnew = specsob[0]
#             updata= specsobnew.jsondata()
#             if update == False:
#                 try:
#                     a = updata[title]
#                     print(a,updata)
#                     messages.error(request,title+" is already exist please change the title")
#                     return redirect('addspecs',id)
#                 except Exception as e:
#                     pass
#             updata[title] = data[title]
#             if oldtitle is not None and oldtitle != title:
#                 updata.pop(oldtitle, None)
#             specsobnew.listele = updata
#             specsobnew.save()
#             redirect('addspecs',id)
#         else:
#             specs(Product=prod,listele=data).save()
#     return render(request, 'superuser/addspecs.html', {'product':prod,"specs":specsob})
# def updatespecs(request,id,update=True):
#     return addspecs(request,id,update=True)
# def deletespecs(request,id,update=True):
#     title = request.GET.get('deltitle')
#     if title is not None:
#         prod = Product.objects.get(id=id)
#         specsob = specs.objects.filter(Product=prod.id)
#         specsobnew = specsob[0]
#         updata= specsobnew.jsondata()
#         updata.pop(title, None)
#         specsobnew.listele = updata
#         specsobnew.save()
#     return redirect('addspecs',id)

# def About(request):
#     res = {}
#     ins = about.objects.all()
#     ins = ins[0] if ins.exists() else None
#     res['form'] = aboutForm(instance=ins)
#     if request.method == 'POST':
#         res['form'] = aboutForm(request.POST,request.FILES,instance=ins)
#         if res['form'].is_valid():
#             res['form'].save()
#             messages.success(request ,'Changes is successfully saved :)')
#     return render(request,'superuser/about.html',res)


# def testdrivebooking(request):
#     res = {}
#     form = GenForm(TestDrive)
#     res['form'] = form()
#     if request.method == "POST":
#         res['form'] = form(request.POST,request.FILES)
#         if res['form'].is_valid():
#             res['form'].save()
#     return render(request,'superuser/testbooking.html',res)
# def alltestdrive(request):
#     res = {}
#     res['testdrives'] = TestDrive.objects.all().order_by('time')
#     return render(request,'superuser/alltestdrive.html',res)
# def contacts(request):
#     res = {}
#     res['contacts'] = Contact.objects.all().order_by('time')
#     return render(request,'superuser/contacts.html',res)
# def addcontact(request):
#     res = {}
#     form = GenForm(Contact)
#     res['form'] = form()
#     if request.method == "POST":
#         res['form'] = form(request.POST,request.FILES)
#         if res['form'].is_valid():
#             res['form'].save()
#     return render(request,'superuser/addcontact.html',res)
# def addinfo(request):
#     res = {}
#     form = GenForm(contactinfo)
#     ins = contactinfo.objects.all()
#     ins = ins[0] if ins.exists() else None
#     res['form'] = form(instance=ins)
#     if request.method == "POST":
#         res['form'] = form(request.POST,request.FILES,instance=ins)
#         if res['form'].is_valid():
#             res['form'].save()
#     return render(request,'superuser/addinfo.html',res)
# def orders(request,slug=None):
#     res = {}
#     res['choices'] = STATUS_CHOICE
#     if slug is None:
#         res['orders'] = OrderPlaced.objects.all().order_by('order_date')
#     else:
#         res['orders'] = OrderPlaced.objects.filter(status=slug).order_by('order_date')
#     return render(request,'superuser/orders.html',res)
# def addorders(request,id=None):
#     res = {}
#     form = GenForm(OrderPlaced)
#     ins = OrderPlaced.objects.filter(id=id)
#     ins = ins[0] if ins.exists() else None
#     res['form'] = form(instance=ins)
#     if request.method == "POST":
#         res['form'] = form(request.POST,request.FILES,instance=ins)
#         if res['form'].is_valid():
#             res['form'].save()
#     return render(request,'superuser/addorders.html',res)


# def users(request,slug=None):
#     res={}
#     if slug is  None:
#         res['users'] = User.objects.all()
#     return render(request,'superuser/users.html',res)
