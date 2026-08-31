from django.urls import path

from . import views

app_name = 'contact'

urlpatterns = [
    path('', views.contact_view, name='contact'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
]
