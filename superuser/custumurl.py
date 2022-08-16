from django.urls import path, include
from .import custumviews as views
urlpatterns = [
    path('',views.sendBulkMail, name="bulksendmail"),
    path('bulkreportupload/',views.bulkreportupload,name="bulkreportupload")
]