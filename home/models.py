from ast import mod
from email import message
from statistics import mode
from django.db import models
from package import models as reqmodel
# Create your models here.
class ContactInfo(models.Model):
    companyname = models.CharField(max_length=100)
    phone = models.CharField(max_length=13)
    helpline = models.CharField(max_length=16)
    email = models.EmailField(default="info@sequeldiagnosticservices.com")
    address = models.TextField()
    def __str__(self) -> str:
        return self.companyname

class customer_contact(models.Model):
    name= models.CharField(max_length=100)
    email= models.CharField(max_length=100)
    mobile= models.CharField(max_length=13)
    subject= models.CharField(max_length=100)
    message= models.TextField()
    def __str__(self) -> str:
        return self.name
class HomeSlider(models.Model):
    name = models.CharField(max_length=50)
    img = models.ImageField(upload_to='slider')
    url = models.CharField(max_length=100,help_text="Copy and Paste The Url of Page your want to redirect")
    def __str__(self) -> str:
        return self.url
    def save(self):
        host = reqmodel.exposed_request.get_host()
        if host in self.url:
            self.url = self.url[self.url.rfind(host)+len(host):] 


    


       
