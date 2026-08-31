from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404

from .models import BlogPost, BlogCategory


def _post_list(request, category=None):
    posts = BlogPost.live.select_related('author', 'category').prefetch_related('tags')
    if category:
        posts = posts.filter(category=category)

    paginator = Paginator(posts, 9)
    page_obj = paginator.get_page(request.GET.get('page'))
    crumbs = [('Insights', '/insights/')] if category else [('Insights', None)]
    if category:
        crumbs.append((category.name, None))
    return render(request, 'blog/list.html', {
        'page_obj': page_obj,
        'categories': BlogCategory.objects.all(),
        'active_category': category,
        'featured_posts': BlogPost.live.filter(featured=True)[:3],
        'crumbs': crumbs,
    })


def post_list(request):
    return _post_list(request)


def post_detail(request, slug):
    post = get_object_or_404(
        BlogPost.live.select_related('author', 'category').prefetch_related('tags'), slug=slug,
    )
    related = BlogPost.live.exclude(pk=post.pk)
    if post.category:
        related = related.filter(category=post.category)
    return render(request, 'blog/detail.html', {
        'post': post, 'related': related[:3],
        'seo_title': post.get_seo_title(post.title),
        'seo_description': post.get_meta_description(post.excerpt),
        'crumbs': [('Insights', '/insights/'), (post.title, None)],
    })


def category_detail(request, slug):
    category = get_object_or_404(BlogCategory, slug=slug)
    return _post_list(request, category=category)
