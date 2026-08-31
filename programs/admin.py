from django.contrib import admin

from .models import Program, ProgramImage


class ProgramImageInline(admin.TabularInline):
    model = ProgramImage
    extra = 1


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'program_type', 'status', 'start_date', 'application_deadline',
        'featured', 'published', 'display_order',
    )
    list_editable = ('display_order', 'featured', 'published')
    list_filter = ('program_type', 'status', 'published', 'featured')
    search_fields = ('title', 'short_description', 'location')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'start_date'
    inlines = [ProgramImageInline]
    actions = ['mark_published', 'mark_unpublished', 'mark_featured']
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'program_type', 'image', 'display_order')}),
        ('Content', {'fields': ('short_description', 'full_description')}),
        ('Schedule & Location', {'fields': (
            ('start_date', 'end_date'), 'application_deadline', 'location', 'status',
        )}),
        ('Call To Action', {'fields': ('cta_text', 'external_application_url')}),
        ('Visibility', {'fields': ('featured', 'published')}),
        ('SEO', {'classes': ('collapse',), 'fields': (
            'seo_title', 'meta_description', 'og_image', 'canonical_url',
            'robots_index', 'robots_follow',
        )}),
    )

    @admin.action(description='Mark selected as published')
    def mark_published(self, request, queryset):
        queryset.update(published=True)

    @admin.action(description='Mark selected as unpublished (draft)')
    def mark_unpublished(self, request, queryset):
        queryset.update(published=False)

    @admin.action(description='Mark selected as featured')
    def mark_featured(self, request, queryset):
        queryset.update(featured=True)
