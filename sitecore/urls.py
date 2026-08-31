from django.urls import path

from . import views

app_name = 'sitecore'

urlpatterns = [
    path('', views.home, name='home'),
    path('gallery/', views.gallery_list, name='gallery'),
    path('search/', views.search, name='search'),
]
