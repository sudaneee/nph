from django.shortcuts import render, get_object_or_404

from organization.models import FounderProfile, CoreValue, WhyChooseFeature
from services.models import Service
from sitecore.models import GalleryImage, SiteSettings

from .models import AboutPage, LegalPage


def about(request):
    about_page = AboutPage.load()
    return render(request, 'pages/about.html', {
        'about_page': about_page,
        'founder': FounderProfile.objects.filter(active=True).first(),
        'core_values': CoreValue.objects.filter(active=True),
        'why_choose_features': WhyChooseFeature.objects.filter(active=True),
        'services': Service.published.all(),
        'gallery_images': GalleryImage.objects.filter(published=True)[:5],
        'seo_title': about_page.get_seo_title(about_page.heading),
        'seo_description': about_page.get_meta_description(SiteSettings.load().tagline),
        'crumbs': [('About', None)],
    })


def legal_page(request, slug):
    page = get_object_or_404(LegalPage, slug=slug)
    return render(request, 'pages/legal.html', {
        'page': page,
        'seo_title': page.get_seo_title(page.title),
        'updated_lead': f'Updated {page.updated_at.strftime("%B %d, %Y")}' if page.content else '',
        'crumbs': [(page.title, None)],
    })
