from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile , EmailVerification
from django.core.mail import send_mail
from django.urls import reverse
import secrets
from django.conf import settings


 

@receiver(post_save, sender=User)
def send_email_verification(sender, instance, created, **kwargs):
    if created :
       

        token = secrets.token_urlsafe(16)
        EmailVerification.objects.create(user=instance, token=token)
        verification_link = reverse('verify_email', args=[token])
        full_link = f"{settings.FRONTEND_URL.rstrip('/')}{verification_link}"

        try:
            send_mail(
                subject='Verify Your Email',
                message=f"""

Hi {instance.first_name},

Thank you for signing up on our ProKit plateform. Please verify your email address by clicking the link below:

{full_link}

If you did not register, please ignore this email.

Best regards,
ProKit
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=False,
            )
        
        except Exception as e:
            pass
           

@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):

    if created:
        Profile.objects.create(user=instance)
    else:
        
        if not hasattr(instance, 'profile'):
            Profile.objects.create(user=instance)
        instance.profile.save()

