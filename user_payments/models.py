from django.db import models
from django.contrib.auth.models import User 

class UserPayments(models.Model):
  app_user = models.ForeignKey(User, on_delete=models.CASCADE)
  subscription_status = models.BooleanField(default=False)
  stripe_checkout_id = models.CharField(max_length=500)
  stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)