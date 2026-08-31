from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from blog.models import BlogPost
from organization.models import (
    FounderProfile, CoreValue, TargetAudience, WhyChooseFeature, ImpactStatistic,
)
from pages.models import AboutPage
from programs.models import Program, PROGRAM_LISTING_TYPES
from services.models import Service

from .models import HeroSlide, HomepageSection, GalleryCategory, GalleryImage


def home(request):
    hero = HeroSlide.objects.filter(active=True).first()
    sections = HomepageSection.objects.filter(enabled=True)
    gallery_images = list(GalleryImage.objects.filter(published=True).select_related('category'))
    core_values = list(CoreValue.objects.filter(active=True))
    values_with_photos = [
        {'value': value, 'photo': gallery_images[i % len(gallery_images)] if gallery_images else None}
        for i, value in enumerate(core_values)
    ]

    context = {
        'hero': hero,
        'sections': sections,
        'about_page': AboutPage.load(),
        'services': Service.published.prefetch_related('features')[:4],
        'core_values': core_values,
        'values_with_photos': values_with_photos,
        'target_audiences': TargetAudience.objects.filter(active=True),
        'why_choose_features': WhyChooseFeature.objects.filter(active=True),
        'founder': FounderProfile.objects.filter(active=True).first(),
        'impact_statistics': ImpactStatistic.objects.filter(active=True),
        'featured_programs': Program.live.filter(program_type__in=PROGRAM_LISTING_TYPES, featured=True)[:3]
                              or Program.live.filter(program_type__in=PROGRAM_LISTING_TYPES)[:3],
        'featured_posts': BlogPost.live.select_related('author', 'category')[:3],
        'gallery_images': gallery_images[:6],
        'featured_gallery_images': [g for g in gallery_images if g.featured][:8] or gallery_images[:8],
        'hero_secondary_image': gallery_images[1] if len(gallery_images) > 1 else (gallery_images[0] if gallery_images else None),
        'image_grid_photos': [
            {'image': img, 'slot': slot}
            for img, slot in zip(gallery_images[2:6], ['a', 'b', 'c', 'd'])
        ],
        'audience_photos': gallery_images[:4],
    }
    return render(request, 'home/home.html', context)


def gallery_list(request):
    images = GalleryImage.objects.filter(published=True).select_related('category')
    categories = GalleryCategory.objects.all()

    category_slug = request.GET.get('category')
    active_category = None
    if category_slug:
        active_category = categories.filter(slug=category_slug).first()
        if active_category:
            images = images.filter(category=active_category)

    paginator = Paginator(images, 24)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'gallery/list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'active_category': active_category,
        'crumbs': [('Gallery', None)],
    })


def search(request):
    query = (request.GET.get('q') or '').strip()
    results = {'services': [], 'programs': [], 'posts': []}
    if query:
        results['services'] = Service.published.filter(
            Q(name__icontains=query) | Q(short_description__icontains=query) | Q(detailed_description__icontains=query)
        )
        results['programs'] = Program.live.filter(
            Q(title__icontains=query) | Q(short_description__icontains=query) | Q(full_description__icontains=query)
        )
        results['posts'] = BlogPost.live.filter(
            Q(title__icontains=query) | Q(excerpt__icontains=query) | Q(content__icontains=query)
        ).select_related('author', 'category')

    total = len(results['services']) + len(results['programs']) + len(results['posts'])
    return render(request, 'pages/search_results.html', {
        'query': query, 'results': results, 'total': total,
    })


def handler404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    return render(request, 'errors/500.html', status=500)
