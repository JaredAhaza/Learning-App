from django.urls import path
from . import views

urlpatterns = [
    path('student_dashboard', views.student_dashboard, name='student_dashboard'),
    path('redirect_to_dashboard', views.redirect_to_dashboard, name='redirect_to_dashboard'),
    path('update_student_profile', views.update_student_profile, name='update_student_profile'),
    path('teacher_dashboard', views.teacher_dashboard, name='teacher_dashboard'),
    path('update_teacher_profile', views.update_teacher_profile, name='update_teacher_profile')
]