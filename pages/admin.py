from django.contrib import admin

from .models import AboutPage, LegalPage


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('heading', 'intro', 'image', 'secondary_image')}),
        ('Call To Action', {'fields': ('cta_text', 'cta_url')}),
        ('SEO', {'classes': ('collapse',), 'fields': (
            'seo_title', 'meta_description', 'og_image', 'canonical_url',
            'robots_index', 'robots_follow',
        )}),
    )

    def has_add_permission(self, request):
        return not AboutPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = AboutPage.load()
        from django.shortcuts import redirect
        return redirect('admin:pages_aboutpage_change', obj.pk)


@admin.register(LegalPage)
class LegalPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'content')}),
        ('SEO', {'classes': ('collapse',), 'fields': (
            'seo_title', 'meta_description', 'og_image', 'canonical_url',
            'robots_index', 'robots_follow',
        )}),
    )
