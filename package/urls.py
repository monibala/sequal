"""sequal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path 
from . import views
urlpatterns = [
    path('testurl/',views.test,name="testurl"),
    path('search/',views.search,name="search"),
    path('getCoupenDetails/',views.getCoupenDetails,name="getCoupenDetails"),
    path('Handlepayment/', views.handlepaytm , name="handlePaytm"),
    path('package/<slug:slug>/', views.packagedetails , name="packagedetails"),
    path('test/<slug:slug>/', views.testdetails , name="testdetails"),
    path('category/<slug:catename>/', views.getbysubcategory , name="getbycategory"),
    path('category/<slug:catename>/<slug:type>/', views.getbysubcategory , name="testcategory"),
    path('subcategory/<slug:subcategory>/', views.getbysubcategory , name="getbysubcategory"),
    path('subcategory/<slug:subcategory>/<slug:type>/', views.getbysubcategory , name="testurl"),
    path('package/<slug:slug>/book-now/<slug:type>', views.booknow , name="booknow"),
]
