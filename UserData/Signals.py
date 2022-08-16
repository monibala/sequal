from django.dispatch import receiver
from threading import Thread
from package import models
from .models import report
from django.db.models.signals import post_save
from superuser.views import getEmailBackend
from django.conf import settings
from django.core.mail import message, send_mail, EmailMessage
@receiver(post_save, sender=report)
def create_profile(sender, instance, created, **kwargs):
    if created:
        email = instance.booking.user.email
        Thread(target=sendmail, args=(instance,email)).start()
def sendmail(instance,to):
    bookingid = instance.booking.Booking_id
    subject = f'Sequal | {bookingid}'
    html_message = "this is your report"
    plain_message = html_message
    to = [to]
    backend , config= getEmailBackend()
    from_email = config.email
    email = EmailMessage(
            subject,
            plain_message,
            from_email,
            to,
            connection=backend
    )
    email.attach("report",instance.report.file.read(),instance.content_type)
    # email.attach_file(settings.MEDIA_ROOT / str(instance.report))
    email.send()