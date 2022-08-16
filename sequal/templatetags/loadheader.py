from os import name
from django import template
from django.db.models import Count
from package.models import category, package
from home.models import ContactInfo
register = template.Library()
@register.filter(name='getcategory')
def getcategory(value):
    return category.objects.all()
@register.filter(name='popularpackage')
def popularpackage(value):
    data =package.objects.annotate(count=Count('Booking__id')).order_by('count')[:16]
    print(len(data),"++++++++")
    return data
    # return package.objects.filter().order_by("Booking__count")
@register.filter(name='getrange')
def getrange(value):
    if len(value)<=1:
        print('retunr')
        return ['0:']
    range1 = f"0:{int(len(value)/2)}"
    range2 = f"{int(len(value)/2)}:"
    return [range1,range2]
@register.filter(name='getContact')
def getContact(value):
    return ContactInfo.objects.all()