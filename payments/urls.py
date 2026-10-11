from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<slug:slug>/', views.checkout, name='checkout'),
    path('callback/<str:reference>/', views.callback, name='callback'),
    path('webhook/zainpay/', views.webhook, name='webhook'),
]
