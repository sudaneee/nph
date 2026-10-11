from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog.models import BlogPost
from learning.models import Course
from programs.models import Program
from services.models import Service


class StaticViewSitemap(Sitemap):
    priority = 0.6
    changefreq = 'monthly'

    def items(self):
        return [
            'sitecore:home', 'pages:about', 'services:list',
            'programs:program_list', 'opportunities:opportunity_list', 'learning:course_list',
            'blog:list', 'contact:contact',
        ]

    def location(self, item):
        return reverse(item)


class ServiceSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Service.published.all()

    def lastmod(self, obj):
        return obj.updated_at


class ProgramSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Program.live.all()

    def lastmod(self, obj):
        return obj.updated_at


class BlogPostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.5

    def items(self):
        return BlogPost.live.all()

    def lastmod(self, obj):
        return obj.updated_at


class CourseSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Course.live.all()

    def lastmod(self, obj):
        return obj.updated_at
