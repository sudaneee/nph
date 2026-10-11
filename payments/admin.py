from django.contrib import admin, messages

from .models import Payment
from .services import confirm_payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('reference', 'user', 'course', 'amount', 'status', 'created_at', 'paid_at')
    list_filter = ('status', 'course')
    search_fields = ('reference', 'user__email', 'user__first_name', 'user__last_name')
    date_hierarchy = 'created_at'
    readonly_fields = ('reference', 'user', 'course', 'amount', 'status', 'gateway_response', 'created_at', 'paid_at')
    actions = ['reverify']

    def has_add_permission(self, request):
        return False

    @admin.action(description='Re-check selected payments with Zainpay')
    def reverify(self, request, queryset):
        results = [confirm_payment(p) for p in queryset.exclude(status='success')]
        self.message_user(request, f'Checked {len(results)} payment(s); {results.count("success")} now successful.',
                          messages.INFO)
