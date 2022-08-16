from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import redirect
from django.urls import resolve
from package import models
from django.urls import reverse
def simple_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        r = resolve(request.path)
        models.exposed_request = request
        appname = r._func_path[:r._func_path.find('.')]
        if appname in ["superuser","UserData"]: #add app name IN LIST  to APPLY middleware in that app
            if appname == "superuser":
                if request.user.is_superuser or request.path==reverse('logindashboard'):
                    response = get_response(request)
                else:
                    rev = reverse('logindashboard') + "?next="+request.get_full_path()
                    response = redirect(rev)
            else:
                if request.user.is_authenticated:
                    if len(request.user.first_name.replace(' ','')) == 0:
                        response = redirect("registration")
                    else:
                        response = get_response(request)
                else:
                    rev = reverse('userlogin') + "?next="+request.get_full_path()
                    response = redirect(rev)
        else:
            response = get_response(request)
        return response
    return middleware