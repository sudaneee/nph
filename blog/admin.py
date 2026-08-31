from django.contrib import admin

from .models import Author, BlogCategory, BlogTag, BlogPost


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'role')
    search_fields = ('name',)


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'published', 'featured', 'published_date')
    list_filter = ('published', 'featured', 'category', 'tags')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ['author', 'category']
    filter_horizontal = ('tags',)
    date_hierarchy = 'published_date'
    actions = ['mark_published', 'mark_unpublished']
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'featured_image', 'author', 'category', 'tags')}),
        ('Content', {'fields': ('excerpt', 'content')}),
        ('Publishing', {'fields': ('published', 'featured', 'published_date')}),
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

