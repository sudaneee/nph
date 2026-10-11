from django.urls import path

from . import views

app_name = 'learning'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('certificates/<str:code>/', views.certificate_verify, name='certificate_verify'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    path('<slug:slug>/learn/', views.course_learn, name='course_learn'),
    path('<slug:slug>/learn/<int:lesson_id>/', views.lesson_view, name='lesson'),
    path('<slug:slug>/learn/<int:lesson_id>/complete/', views.complete_lesson, name='complete_lesson'),
    path('<slug:slug>/quiz/<int:quiz_id>/', views.quiz_view, name='quiz'),
    path('<slug:slug>/certificate/', views.certificate, name='certificate'),
]
