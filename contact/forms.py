from django import forms

from .models import ContactMessage, NewsletterSubscriber


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'organization', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your full name', 'autocomplete': 'name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'you@example.com', 'autocomplete': 'email'}),
            'phone': forms.TextInput(attrs={'placeholder': '+234 800 000 0000', 'autocomplete': 'tel'}),
            'organization': forms.TextInput(attrs={'placeholder': 'Company / organization (optional)'}),
            'subject': forms.TextInput(attrs={'placeholder': 'How can we help?'}),
            'message': forms.Textarea(attrs={'placeholder': 'Tell us more…', 'rows': 6}),
        }

    def clean_name(self):
        return self.cleaned_data['name'].strip()

    def clean_subject(self):
        return self.cleaned_data['subject'].strip()

    def clean_message(self):
        message = self.cleaned_data['message'].strip()
        if len(message) < 10:
            raise forms.ValidationError('Please provide a little more detail (at least 10 characters).')
        return message


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email', 'name']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Your email address', 'autocomplete': 'email'}),
            'name': forms.HiddenInput(),
        }

    def clean_email(self):
        return self.cleaned_data['email'].strip().lower()
