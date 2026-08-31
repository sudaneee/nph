from django.urls import path

from . import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.about, name='about'),
    path('<slug:slug>/', views.legal_page, name='legal'),
]
