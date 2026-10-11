from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_email', 'phone')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'phone')
    raw_id_fields = ('user',)

    @admin.display(description='Email', ordering='user__email')
    def user_email(self, obj):
        return obj.user.email
