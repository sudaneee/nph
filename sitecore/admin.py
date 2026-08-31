from django.contrib import admin

from .models import (
    SiteSettings, NavigationItem, FooterLink, SocialLink,
    HeroSlide, HomepageSection, CTASection, GalleryCategory, GalleryImage,
)

admin.site.site_header = 'Northpreneur Hub — Admin'
admin.site.site_title = 'Northpreneur Hub Admin'
admin.site.index_title = 'Website Control Panel'


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Identity', {'fields': ('site_name', 'tagline', 'logo', 'logo_dark', 'favicon')}),
        ('Contact Details', {'fields': ('phone_primary', 'phone_secondary', 'email', 'address', 'map_embed_url')}),
        ('Mission & Vision', {'fields': ('mission_statement', 'vision_statement')}),
        ('Footer', {'fields': ('footer_about', 'copyright_text')}),
        ('Default SEO', {
            'classes': ('collapse',),
            'fields': ('default_seo_title', 'default_meta_description', 'default_og_image', 'google_analytics_id'),
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.load()
        from django.shortcuts import redirect
        return redirect('admin:sitecore_sitesettings_change', obj.pk)


@admin.register(NavigationItem)
class NavigationItemAdmin(admin.ModelAdmin):
    list_display = ('label', 'url', 'is_cta', 'active', 'display_order')
    list_editable = ('display_order', 'active')
    list_filter = ('active', 'is_cta')
    search_fields = ('label', 'url')


@admin.register(FooterLink)
class FooterLinkAdmin(admin.ModelAdmin):
    list_display = ('label', 'group', 'url', 'active', 'display_order')
    list_editable = ('display_order', 'active')
    list_filter = ('group', 'active')
    search_fields = ('label', 'url')


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ('platform', 'url', 'active', 'display_order')
    list_editable = ('display_order', 'active')
    list_filter = ('active',)


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ('headline', 'active', 'updated_at')
    list_filter = ('active',)
    fieldsets = (
        (None, {'fields': ('active', 'badge_text', 'headline', 'subheadline', 'background_image')}),
        ('Buttons', {'fields': (
            ('primary_cta_text', 'primary_cta_url'),
            ('secondary_cta_text', 'secondary_cta_url'),
        )}),
        ('Stat Strip', {
            'description': 'The small "04 / Core Service Areas" style strip beneath the buttons. Leave a value blank to hide that item.',
            'fields': (
                ('stat1_value', 'stat1_label'),
                ('stat2_value', 'stat2_label'),
                ('stat3_value', 'stat3_label'),
            ),
        }),
        ('Photo Collage Label', {
            'description': 'The floating badge on the hero photo (e.g. "Skills to Income").',
            'fields': ('collage_label_title', 'collage_label_subtitle'),
        }),
    )


@admin.register(HomepageSection)
class HomepageSectionAdmin(admin.ModelAdmin):
    list_display = ('section_type', 'title', 'background_style', 'enabled', 'display_order')
    list_editable = ('display_order', 'enabled')
    list_filter = ('enabled', 'background_style')
    fieldsets = (
        (None, {'fields': ('section_type', 'enabled', 'display_order', 'background_style')}),
        ('Content Overrides', {
            'description': 'Optional — leave blank to use the section’s default heading/copy.',
            'fields': ('title', 'subtitle', 'description', 'image'),
        }),
    )


@admin.register(CTASection)
class CTASectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'active', 'updated_at')
    list_filter = ('active',)


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'display_order')
    list_editable = ('display_order',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date', 'featured', 'published', 'display_order')
    list_editable = ('display_order', 'featured', 'published')
    list_filter = ('category', 'featured', 'published')
    search_fields = ('title', 'caption', 'description')
    autocomplete_fields = ['category']
    date_hierarchy = 'date'
    fieldsets = (
        (None, {'fields': ('title', 'image', 'category', 'date', 'display_order')}),
        ('Content', {'fields': ('description', 'caption', 'alt_text')}),
        ('Visibility', {'fields': ('featured', 'published')}),
    )
