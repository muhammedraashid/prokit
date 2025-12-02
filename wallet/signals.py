from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Wallet
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def manage_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)
    else:
        if not hasattr(instance, "wallet"):
            Wallet.objects.create(user=instance)
        else:
            instance.wallet.save()
