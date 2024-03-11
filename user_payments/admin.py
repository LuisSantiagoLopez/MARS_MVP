from django.contrib import admin
from .models import UserPayments

class UserPaymentsAdmin(admin.ModelAdmin):
    list_display = ('app_user', 'subscription_name', 'subscription_status', 'checkout_id', 'subscription_id', 'customer_id', 'created_at')
    list_filter = ('subscription_status', 'created_at')
    search_fields = ('app_user__username', 'customer_id', 'subscription_id')
    list_display_links = ('app_user', 'subscription_id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'subscription_id')

    def get_readonly_fields(self, request, obj=None):
        if obj: 
            return self.readonly_fields + ('app_user', 'customer_id')
        return self.readonly_fields


admin.site.register(UserPayments, UserPaymentsAdmin)
