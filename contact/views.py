from django.contrib import messages
from django.core.mail import mail_admins
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import ContactForm, NewsletterForm


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            try:
                mail_admins(
                    subject=f'New contact message: {contact_message.subject}',
                    message=(
                        f'From: {contact_message.name} <{contact_message.email}>\n'
                        f'Organization: {contact_message.organization or "—"}\n'
                        f'Phone: {contact_message.phone or "—"}\n\n'
                        f'{contact_message.message}'
                    ),
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, "Thank you — your message has been received. We'll be in touch shortly.")
            return redirect(reverse('contact:contact'))
    else:
        form = ContactForm()

    return render(request, 'contact/contact.html', {'form': form, 'crumbs': [('Contact', None)]})


@require_POST
def newsletter_subscribe(request):
    form = NewsletterForm(request.POST)
    next_url = request.POST.get('next') or reverse('sitecore:home')
    if form.is_valid():
        email = form.cleaned_data['email']
        from .models import NewsletterSubscriber
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email, defaults={'name': form.cleaned_data.get('name', '')},
        )
        if not created and not subscriber.active:
            subscriber.active = True
            subscriber.save(update_fields=['active'])
        if created:
            messages.success(request, "You're subscribed! Thanks for joining our newsletter.")
        else:
            messages.info(request, "You're already on our newsletter list.")
    else:
        messages.error(request, 'Please enter a valid email address.')
    return redirect(next_url)
