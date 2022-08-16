
from django.urls import path 
from . import views
urlpatterns = [
    path('dashboard/',views.dashboard,name="userdashboard"),
    # path('subscription/',userView.subscription,name="subscription"),
    path('profile/',views.profile,name="profile"),
    path('booking/',views.booking,name="booking"),
    path('report/',views.Report,name="report"),
    path('report/report<slug:slug>/download',views.Report,name="reportdownload"),
    path('family/',views.family,name="family"),
    path('getmember/',views.getMember,name="getmember"),
    path('deletemember/<int:id>',views.deleteMember,name="deletemember"),
    path('address/',views.address,name="address"),
    path('getaddress/',views.getaddress,name="getaddress"),
    path('deleteaddress/<int:id>/',views.deleteaddress,name="deleteaddress"),
    path('upload-prescription/',views.uploadprescription,name="uploadprescription"),
 
]
