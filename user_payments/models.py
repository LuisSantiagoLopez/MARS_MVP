from django.db import models
from django.contrib.auth.models import User 
from django.dispatch import receiver
from django.db.models.signals import post_save


class UserPayments(models.Model):
  app_user = models.ForeignKey(User, on_delete=models.CASCADE)
  payment_bool = models.BooleanField(default=False)
  stripe_subscription_id = models.CharField(max_length=500)
  stripe_customer_id = models.CharField(max_length=255, null=True, blank=True) 


@receiver(post_save, sender=User)
def create_user_payment(sender, instance, created, **kwargs):
  if created:
    UserPayments.objects.create(app_user=instance)