
from django.db import models

# Create your models here.
class PaytmConfig(models.Model):
    title = models.CharField(max_length=100,help_text='add mode for example "( testing config )" ')
    activate = models.BooleanField(help_text=":- check to activate",default=False)
    MID = models.CharField(max_length=100)
    MERCHANT_KEY = models.CharField(max_length=100)
    WEBSITE = models.CharField(max_length=100,choices=(('1','WEBSTAGING'),('2','DEFAULT')),help_text="choose Webstaging for testiing and Default for production")
    PostUrl = models.CharField(max_length=1000, blank=True)
    def __str__(self):
        return self.title
    stage = "https://securegw-stage.paytm.in/order/process"
    production = "https://securegw.paytm.in/order/process"
    def save(self, *args, **kwargs):
        if self.activate:
            data=PaytmConfig.objects.all().exclude(id=self.id)
            data.update(activate=False)
        self.PostUrl = self.production if self.WEBSITE == '2' else self.stage
        super(PaytmConfig, self).save(*args, **kwargs)
class rozpayConfig(models.Model):
    title = models.CharField(max_length=100,help_text='add mode for example "( testing config )" ')
    activate = models.BooleanField(help_text=":- check to activate",default=False)
    RAZOR_KEY_ID = models.CharField(max_length=200)
    RAZOR_KEY_SECRET = models.CharField(max_length=200)
    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        if self.activate:
            data=rozpayConfig.objects.all().exclude(id=self.id)
            data.update(activate=False)
        super(rozpayConfig, self).save(*args, **kwargs)
class paypalConfig(models.Model):
    title = models.CharField(max_length=100,help_text='add mode for example "( testing config )" ')
    RECEIVER_EMAIL = models.CharField(max_length=100)
    test = models.BooleanField(help_text=":- check If you want to test payment method",default=False)
    activate = models.BooleanField(help_text=":- check to activate",default=False)
    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        if self.activate:
            data=paypalConfig.objects.all().exclude(id=self.id)
            data.update(activate=False)
        super(paypalConfig, self).save(*args, **kwargs)

class PaytmTransaction(models.Model):
    ORDERID = models.CharField(max_length=50,blank=True)
    TXNID = models.CharField(max_length=50,blank=True)
    STATUS = models.CharField(max_length=50,blank=True)
    TXNAMOUNT = models.CharField(max_length=50,blank=True)
    CURRENCY = models.CharField(max_length=4,blank=True)
    GATEWAYNAME = models.CharField(max_length=15,blank=True)
    RESPMSG = models.CharField(max_length=50,blank=True)
    BANKNAME = models.CharField(max_length=50,blank=True)
    PAYMENTMODE = models.CharField(max_length=50,blank=True)
    MID = models.CharField(max_length=50,blank=True)
    RESPCODE = models.CharField(max_length=50,blank=True)
    BANKTXNID = models.CharField(max_length=50,blank=True)
    TXNDATE = models.DateTimeField()
    CHECKSUMHASH = models.CharField(max_length=50,blank=True)
    def __str__(self) -> str:
        return super().__str__()
