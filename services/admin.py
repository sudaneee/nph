from django.contrib import admin

from .models import Service, ServiceFeature


class ServiceFeatureInline(admin.TabularInline):
    model = ServiceFeature
    extra = 1


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'featured', 'active', 'display_order')
    list_editable = ('display_order', 'featured', 'active')
    list_filter = ('active', 'featured')
    search_fields = ('name', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ServiceFeatureInline]
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'icon', 'image', 'display_order', 'featured', 'active')}),
        ('Content', {'fields': ('short_description', 'detailed_description')}),
        ('Call To Action', {'fields': ('cta_text', 'cta_url')}),
        ('SEO', {'classes': ('collapse',), 'fields': (
            'seo_title', 'meta_description', 'og_image', 'canonical_url',
            'robots_index', 'robots_follow',
        )}),
    )
