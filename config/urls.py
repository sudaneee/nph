from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.views.generic import TemplateView

from sitecore.sitemaps import StaticViewSitemap, ServiceSitemap, ProgramSitemap, BlogPostSitemap
from programs.urls import opportunity_urlpatterns

sitemaps = {
    'static': StaticViewSitemap,
    'services': ServiceSitemap,
    'programs': ProgramSitemap,
    'blog': BlogPostSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),

    path('', include('sitecore.urls')),
    path('services/', include('services.urls')),
    path('programs/', include('programs.urls')),
    path('opportunities/', include((opportunity_urlpatterns, 'programs'), namespace='opportunities')),
    path('insights/', include('blog.urls')),
    path('contact/', include('contact.urls')),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name='robots'),

    # pages.urls is mounted last: its trailing `<slug:slug>/` catch-all (for
    # admin-authored legal pages) must never shadow the explicit prefixes above.
    path('', include('pages.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'sitecore.views.handler404'
handler500 = 'sitecore.views.handler500'
