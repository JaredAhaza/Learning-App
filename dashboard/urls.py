from django.urls import path
from . import views

urlpatterns = [
    path('student_dashboard', views.student_dashboard, name='student_dashboard'),
    path('update_student_profile', views.update_student_profile, name='update_student_profile'),
    path('student_profile', views.student_profile, name='student_profile'),
]