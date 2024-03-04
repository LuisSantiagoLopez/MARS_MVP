from django.contrib import admin
from .models import UserPayments

class UserPaymentsAdmin(admin.ModelAdmin):
    list_display = ('app_user', 'subscription_type', 'subscription_status', 'stripe_checkout_id', 'stripe_customer', 'created_at')
    list_filter = ('subscription_status', 'created_at')
    search_fields = ('app_user__username', 'stripe_customer', 'stripe_checkout_id')
    list_display_links = ('app_user', 'stripe_checkout_id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'stripe_checkout_id')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('app_user', 'stripe_customer')
        return self.readonly_fields

# Unregister the model if it was previously registered
admin.site.unregister(UserPayments)

# Register the model with the custom admin class
admin.site.register(UserPayments, UserPaymentsAdmin)
