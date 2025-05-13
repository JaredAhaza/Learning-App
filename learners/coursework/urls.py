from django.urls import path
from . import views

urlpatterns = [
    path('add_course', views.add_course, name='add_course'),
    path('course_list', views.course_list, name='course_list'),
]