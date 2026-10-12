import re

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


def head(resp):
    return resp.content.decode().split('</head>')[0]


class SeoBlockTests(TestCase):
    """Per-page SEO blocks must reach the <head> (they silently didn't when they lived in an include)."""

    def test_pages_render_their_own_title(self):
        for url, expected in [(reverse('contact:contact'), 'Contact —'),
                              (reverse('learning:course_list'), 'Online Courses —'),
                              (reverse('accounts:login'), 'Log in —')]:
            title = re.search(r'<title>(.*?)</title>', head(self.client.get(url)), re.S).group(1)
            self.assertIn(expected, title, url)

    def test_noindex_pages_say_so(self):
        resp = self.client.get(reverse('sitecore:search') + '?q=x')
        self.assertIn('content="noindex, follow"', head(resp))
        self.assertIn('content="index, follow"', head(self.client.get(reverse('contact:contact'))))

    def test_student_portal_is_noindex_and_titled(self):
        user = get_user_model().objects.create_user('p', email='p@example.com', password='pw')
        self.client.force_login(user)
        h = head(self.client.get(reverse('accounts:dashboard')))
        self.assertIn('content="noindex, follow"', h)
        self.assertIn('<title>My Learning —', h)

    def test_no_template_syntax_leaks_into_head(self):
        h = head(self.client.get(reverse('contact:contact')))
        self.assertNotIn('{%', h)
        self.assertNotIn('{#', h)
        self.assertNotIn('SEO tags live here', h)
