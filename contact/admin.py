from django.contrib import admin

from .models import ContactMessage, NewsletterSubscriber


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'email', 'is_read', 'is_responded', 'created_at')
    list_filter = ('is_read', 'is_responded', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message', 'organization')
    readonly_fields = ('name', 'email', 'phone', 'organization', 'subject', 'message', 'created_at')
    fieldsets = (
        ('Submission', {'fields': (
            'created_at', 'name', 'email', 'phone', 'organization', 'subject', 'message',
        )}),
        ('Status', {'fields': ('is_read', 'is_responded', 'internal_notes')}),
    )
    actions = ['mark_read', 'mark_responded']
    date_hierarchy = 'created_at'

    @admin.action(description='Mark selected as read')
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description='Mark selected as responded')
    def mark_responded(self, request, queryset):
        queryset.update(is_responded=True, is_read=True)


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'active', 'subscribed_at')
    list_filter = ('active',)
    search_fields = ('email', 'name')
    date_hierarchy = 'subscribed_at'
