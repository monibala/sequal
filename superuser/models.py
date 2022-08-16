from django.db import models

from ckeditor_uploader.fields import RichTextUploadingField
# Create your models here.
class aboutContact(models.Model):
    logo = models.ImageField(upload_to="logo")
    AdminTitle = models.CharField(max_length=30)
    favicon  = models.ImageField(upload_to='logo')
    

class emailSetup(models.Model):
    host = models.CharField(max_length=100)
    port = models.IntegerField()
    email = models.CharField(max_length=100)
    tsl = models.BooleanField()
    ssl = models.BooleanField()
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    activate = models.BooleanField(help_text="other mail is automatically disabled")
    def save(self, *args, **kwargs):
        if self.activate:
            data=emailSetup.objects.all().exclude(id=self.id)
            data.update(activate=False)
        super(emailSetup, self).save(*args, **kwargs)