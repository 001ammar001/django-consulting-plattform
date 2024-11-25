from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from ..models import Wallet

User = settings.AUTH_USER_MODEL

@receiver(post_save,sender=User)
def create_wallet_for_user(sender,**kwargs):
   print('signas')
   if kwargs['created']:
      Wallet.objects.create(user=kwargs['instance'])