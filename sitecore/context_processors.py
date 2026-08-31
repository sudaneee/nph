from .models import SiteSettings, NavigationItem, FooterLink, SocialLink, CTASection


def site_context(request):
    """Site-wide data available to every template: settings, nav, footer, socials, CTA."""
    return {
        'site_settings': SiteSettings.load(),
        'nav_items': NavigationItem.objects.filter(active=True),
        'footer_links': FooterLink.objects.filter(active=True),
        'social_links': SocialLink.objects.filter(active=True),
        'cta_section': CTASection.objects.filter(active=True).first(),
    }
