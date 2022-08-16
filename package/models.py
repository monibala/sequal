
from distutils.command.upload import upload
from email import message
from email.policy import default
from math import fabs
from operator import mod
from pydoc import describe
from statistics import mode
from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.
# from UserData.models import User

exposed_request = None

import random,string
from django.utils.text import slugify

# Create your models here.
def get_random_string(size):
    return ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k = size))

def unique_slug_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance 
    has a model with a slug field and a title character (char) field.
    """
    slug=slugify(new_slug)[:50]
    Klass = instance
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = slugify(str(slug)[:46]+get_random_string(4))
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug

class category(models.Model):
    name = models.CharField(max_length=100,unique=True)
    describe = models.CharField(max_length=100)
    img = models.ImageField(upload_to="images",blank=True,help_text="optional")
    slug = models.SlugField(blank=True)
    def __str__(self) -> str:
        return self.name
    def save(self, *args, **kwargs):
        if self.id is None or self.slug is None or len(self.slug)==0:
            self.slug = unique_slug_generator(category,self.name)
        super().save()
class Subcategory(models.Model):
    category = models.ForeignKey(category,on_delete=models.CASCADE,related_name="subcategory" )
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True)
    logo = models.ImageField(upload_to="logos",default="logos/logo.png")
    shortdes = models.TextField(blank=True)
    description = RichTextUploadingField(blank=True)
    class Meta:
        unique_together = ('category', 'name',)
    def __str__(self) -> str:
        return f"{self.name} ({self.category.name})"
    def save(self, *args, **kwargs):
        if self.id is None or self.slug is None or len(self.slug)==0:
            self.slug = unique_slug_generator(Subcategory,self.name)
        super().save()


class test(models.Model):
    test_uniqueId = models.CharField(max_length=50, blank=True)
    test_name = models.CharField(max_length = 50)
    test_description = RichTextUploadingField()
    test_category = models.ManyToManyField(Subcategory,blank=True,related_name="test")
    test_price  = models.FloatField()
    sample_colllection_charges = models.CharField(max_length = 1,choices=(("1","Yes"),("0","No")))
    discount = models.CharField(help_text="You Can Ammount or Percent of Ammount Eg: 100 or 10%",max_length=10)
    final_cost  = models.FloatField(max_length = 50,blank=True)
    Publish = models.CharField(max_length = 1,choices=(("1","Yes"),("0","No")))
    slug = models.SlugField(blank=True)
        
    def __str__(self):
        return F"{self.test_name} - ( {self.test_uniqueId} )"
    def delete(self):
        data = self.profile.all()
        if len(data)>0:
            message = "Unable to delete This test is used in these Profile [ "
            for d in data:
                message+= str(d)+", "
            message+= " ] please remove it first.."
            raise ValidationError(message)
        return super().delete()
    def save(self, *args, **kwargs):
        if self.discount:
            if self.id is None or len(self.slug)==0:
                self.slug = unique_slug_generator(package,self.test_name)
            discount = float(self.discount.replace("%",''))
            if '%' in self.discount:
                self.final_cost = self.test_price -((self.test_price*discount)/100)
            else:
                self.final_cost = self.test_price - discount
        super(test, self).save(*args, **kwargs)
        if len(self.test_uniqueId)<1:
            self.test_uniqueId = "Stest"+F"{self.id}"
        super(test, self).save(*args, **kwargs)
    def clean(self):
        discount = self.discount.replace('%','')
        try:
            discount = float(discount)
        except:
            raise ValidationError(
                {'discount': "Please add a valid discount"})
        if '%' in self.discount:
            if not (discount <=100):
                raise ValidationError(
                {'discount': "discount should be under 100%"})
        else:
            if discount>self.test_price:
                raise ValidationError(
                {'discount': "discount should be less than test Prize"})


class profile(models.Model):
    Profile_Id = models.CharField(max_length=50,blank = True)
    Profile_Name = models.CharField(max_length=50)
    Select_Test_id = models.ManyToManyField(test,related_name="profile")
    profile_description = models.TextField()
    Publish = models.CharField(max_length = 1,choices=(("1","Yes"),("0","No")))
    
    def save(self, *args, **kwargs):
        super(profile, self).save(*args, **kwargs)
        if len(self.Profile_Id)<1:
            self.Profile_Id = "Sprofile"+F"{self.id}"
        super(profile, self).save(*args, **kwargs)
    def __str__(self):
        return F"{self.Profile_Name} - ( {self.Profile_Id} )"
class PackageAvailablefor(models.Model):
    gender = models.CharField(max_length=20)
    def __str__(self):
        return self.gender


class package(models.Model):
    Package_id = models.CharField(max_length=50,blank=True)
    Package_name = models.CharField(max_length=50)
    package_category = models.ManyToManyField(Subcategory,blank=True,related_name="package")
    Porfile_collection = models.ManyToManyField(profile,related_name='package')
    Package_descrption = RichTextUploadingField()
    Package_price = models.FloatField()
    Package_for = models.ManyToManyField(PackageAvailablefor)
    discount = models.CharField(help_text="You Can Ammount or Percent of Ammount Eg: 100 or 10%",max_length=10)
    final_cost  = models.FloatField(max_length = 50,blank=True)
    popular_package = models.BooleanField(default=False)
    Publish = models.CharField(max_length = 1,choices=(("1","Yes"),("0","No")))
    slug = models.SlugField(blank=True)
    def __str__(self):
        return F"{self.Package_name} - ( {self.Package_id} )"
    def save(self, *args, **kwargs):
        if self.id is None:
            self.slug = unique_slug_generator(package,self.Package_name)
        if self.discount:
            discount = float(self.discount.replace("%",''))
            if '%' in self.discount:
                self.final_cost = self.Package_price -((self.Package_price*discount)/100)
            else:
                self.final_cost = self.Package_price - discount
            self.final_cost = "{:.2f}".format(self.final_cost)
        super(package, self).save(*args, **kwargs)
        if len(self.Package_id)<1:
            self.Package_id = "Package"+F"{self.id}"
        super(package, self).save(*args, **kwargs)
    def clean(self):
        discount = self.discount.replace('%','')
        try:
            discount = float(discount)
        except:
            raise ValidationError(
                {'discount': "Please add a valid discount"})
        if '%' in self.discount:
            if not (discount <=100):
                raise ValidationError(
                {'discount': "discount should be under 100%"})
        else:
            if discount>self.Package_price:
                raise ValidationError(
                {'discount': "discount should be less than test Prize"})


class coupon(models.Model):
    Coupon_id = models.CharField(max_length=50,blank=True)
    coupan_name = models.CharField(max_length=50)
    Generate_coupon = models.CharField(max_length=50,help_text="Add coupon or leave blank to genrate automatically..",blank=True,unique=True)
    Coupon_expire_date = models.DateField()
    quantity = models.IntegerField(default=100)
    used = models.IntegerField(default=0)
    remaining = models.IntegerField(default=0)
    Coupon_partical_allowes = models.CharField(max_length = 1,choices=(("1","Yes"),("0","No")))
    Coupon_issed_by = models.ForeignKey('UserData.User',on_delete=models.SET_NULL,null=True,blank=True)
    Coupon_created = models.DateField(auto_now=True) 
    message = models.CharField(max_length=100,help_text="User will see this messge when he/she apply the coupen",default='Applied')
    discount = models.CharField(help_text="You Can Ammount or Percent of Ammount Eg: 100 or 10%",max_length=10)
    minimum_order_value = models.FloatField()
    active = models.CharField(max_length = 1,choices=(("1","Yes"),("0","No")))
    def __str__(self):
        return F"{self.coupan_name} - ( {self.Coupon_id} )"
    def save(self, *args, **kwargs):
        self.Coupon_issed_by = exposed_request.user
        self.remaining = self.quantity - self.used
        super(coupon, self).save(*args, **kwargs)
        if len(self.Coupon_id)<1:
            self.Coupon_id = "Package"+F"{self.id}"
        super(coupon, self).save(*args, **kwargs)
    def clean(self):
        discount = self.discount.replace('%','')
        try:
            discount = float(discount)
        except:
            raise ValidationError(
                {'discount': "Please add a valid discount"})
        if '%' in self.discount:
            if not (discount <=100):
                raise ValidationError(
                {'discount': "discount should be under 100%"})


class Faqs(models.Model):
    package = models.ForeignKey(package,on_delete=models.CASCADE , related_name="Faqs")
    question = models.CharField(max_length=150)
    Answere = models.TextField()
    def __str__(self):
        return F"{self.question}" 
class tempbooking(models.Model):
    user = models.ForeignKey('UserData.User',blank=True,on_delete=models.SET_NULL,null=True,related_name='tempbooking')
    bookingid = models.ManyToManyField("UserData.Booking",related_name="Transtaction") #csv formate
    # bookingid = models.TextField() #csv formate
    tempbookingid = models.CharField(max_length=20)
    coupon = models.CharField(max_length=50,blank=True)
    ammount = models.CharField(max_length=20)
    status = models.CharField(max_length=10,choices=(('success','success'),('pending','pending')),default="pending")
    def __str__(self):
        return F"{self.tempbookingid}"
    def save(self, ) -> None:
        if self.id is None:
            now = datetime.now()
            super().save()
            self.tempbookingid = f'sequel{now.year}{now.month}{now.day}{self.id}'.upper()
        super().save()