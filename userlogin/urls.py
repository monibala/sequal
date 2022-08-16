
from django.urls import path 
from . import views
urlpatterns = [
    path('login', views.LoginSignUp , name="userlogin"),
    path('login/verifyotp', views.verifyotp , name="verifyotp"),
    path('registration/',views.registration,name="registration"),
    path('logout/',views.Logout,name="logoutuser"),
]
