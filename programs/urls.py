from django.urls import path

from . import views

app_name = 'programs'

urlpatterns = [
    path('', views.program_list, name='program_list'),
    path('<slug:slug>/', views.program_detail, name='program_detail'),
]

opportunity_urlpatterns = [
    path('', views.opportunity_list, name='opportunity_list'),
    path('<slug:slug>/', views.opportunity_detail, name='opportunity_detail'),
]
