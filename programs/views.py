from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404

from .models import Program, PROGRAM_LISTING_TYPES, OPPORTUNITY_LISTING_TYPES


def program_list(request):
    programs = Program.live.filter(program_type__in=PROGRAM_LISTING_TYPES).prefetch_related('gallery')
    paginator = Paginator(programs, 9)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'programs/program_list.html', {
        'page_obj': page_obj, 'crumbs': [('Programs', None)],
    })


def program_detail(request, slug):
    program = get_object_or_404(
        Program.live.filter(program_type__in=PROGRAM_LISTING_TYPES).prefetch_related('gallery'), slug=slug,
    )
    related = Program.live.filter(program_type__in=PROGRAM_LISTING_TYPES).exclude(pk=program.pk)[:3]
    return render(request, 'programs/program_detail.html', {
        'program': program, 'related': related,
        'seo_title': program.get_seo_title(program.title),
        'seo_description': program.get_meta_description(program.short_description),
        'crumbs': [('Programs', '/programs/'), (program.title, None)],
    })


def opportunity_list(request):
    opportunities = Program.live.filter(program_type__in=OPPORTUNITY_LISTING_TYPES).prefetch_related('gallery')
    paginator = Paginator(opportunities, 9)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'programs/opportunity_list.html', {
        'page_obj': page_obj, 'crumbs': [('Opportunities', None)],
    })


def opportunity_detail(request, slug):
    opportunity = get_object_or_404(
        Program.live.filter(program_type__in=OPPORTUNITY_LISTING_TYPES).prefetch_related('gallery'), slug=slug,
    )
    related = Program.live.filter(program_type__in=OPPORTUNITY_LISTING_TYPES).exclude(pk=opportunity.pk)[:3]
    return render(request, 'programs/opportunity_detail.html', {
        'opportunity': opportunity, 'related': related,
        'seo_title': opportunity.get_seo_title(opportunity.title),
        'seo_description': opportunity.get_meta_description(opportunity.short_description),
        'crumbs': [('Opportunities', '/opportunities/'), (opportunity.title, None)],
    })
