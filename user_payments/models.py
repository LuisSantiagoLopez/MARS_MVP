from django.db import models
from django.contrib.auth.models import User 

class UserPayments(models.Model):
    app_user = models.ForeignKey(User, on_delete=models.CASCADE)
    upgrade = models.BooleanField(default=False)
    last_payment_subscription_id = models.CharField(max_length=255, null=True, blank=True)
    price_id = models.CharField(max_length=255, null=True, blank=True)
    subscription_name = models.CharField(max_length=255, null=True, blank=True)
    subscription_status = models.BooleanField(default=False)
    checkout_id = models.CharField(max_length=500)
    subscription_id = models.CharField(max_length=500)
    customer_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CostPerUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    accumulated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cost_instance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    available_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    model = models.CharField(max_length=255, null=True, blank=True)
    use_case = models.CharField(max_length=500)
    context_tokens = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    output_tokens = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    timestamp = models.DateTimeField(auto_now_add=True)