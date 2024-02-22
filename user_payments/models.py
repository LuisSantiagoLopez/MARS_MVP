from django.db import models
from django.contrib.auth.models import User 
from django.dispatch import receiver
from django.db.models.signals import post_save


class UserPayments(models.Model):
  app_user = models.ForeignKey(User, on_delete=models.CASCADE)
  payment_bool = models.BooleanField(default=False)
  stripe_checkout_id = models.CharField(max_length=500)
  stripe_customer_id = models.CharField(max_length=255, null=True, blank=True) 
