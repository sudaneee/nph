from django.shortcuts import render, get_object_or_404

from .models import Service


def service_list(request):
    services = Service.published.prefetch_related('features')
    return render(request, 'services/list.html', {'services': services})


def service_detail(request, slug):
    service = get_object_or_404(Service.published.prefetch_related('features'), slug=slug)
    other_services = Service.published.exclude(pk=service.pk)[:3]
    return render(request, 'services/detail.html', {
        'service': service,
        'other_services': other_services,
        'seo_title': service.get_seo_title(service.name),
        'seo_description': service.get_meta_description(service.short_description),
        'crumbs': [('Services', '/services/'), (service.name, None)],
    })
