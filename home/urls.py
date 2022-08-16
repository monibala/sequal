from  django.urls import path
from django.urls.resolvers import URLPattern
from .import views
urlpatterns=[
    path('',views.index,name='index'),
    path('contact/',views.contact,name='contact'),
    path('callback/',views.callback,name='callback'),
    path('aboutus/', views.aboutus,name='aboutus')
]