from django.contrib import admin

from .models import (
    FounderProfile, TeamMember, CoreValue, TargetAudience,
    WhyChooseFeature, ImpactStatistic, Testimonial, FAQ,
)


@admin.register(FounderProfile)
class FounderProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'active')
    fields = ('active', 'name', 'position', 'photo', 'message', 'linkedin_url')

    def has_add_permission(self, request):
        return not FounderProfile.objects.exists()


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'active', 'display_order')
    list_editable = ('display_order', 'active')
    list_filter = ('active',)
    search_fields = ('name', 'role')


@admin.register(CoreValue)
class CoreValueAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'display_order')
    list_editable = ('display_order', 'active')
    list_filter = ('active',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(TargetAudience)
class TargetAudienceAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'active', 'display_order')
    list_editable = ('display_order', 'active')
    list_filter = ('active',)


@admin.register(WhyChooseFeature)
class WhyChooseFeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'active', 'display_order')
    list_editable = ('display_order', 'active')
    list_filter = ('active',)


@admin.register(ImpactStatistic)
class ImpactStatisticAdmin(admin.ModelAdmin):
    list_display = ('label', 'number', 'active', 'display_order')
    list_editable = ('display_order', 'active')
    list_filter = ('active',)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'role_organization', 'active', 'display_order')
    list_editable = ('display_order', 'active')
    list_filter = ('active',)
    search_fields = ('name', 'role_organization')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'active', 'display_order')
    list_editable = ('display_order', 'active')
    list_filter = ('active',)
    search_fields = ('question', 'answer')
