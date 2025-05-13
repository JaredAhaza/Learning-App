from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView    

urlpatterns = [
    path('studentlogin', LoginView.as_view(template_name='accounts/studentlogin.html'), name='studentlogin'),
    path('studentregister', views.studentregister, name='studentregister'),
    path('student_logout', views.student_logout_view, name='student_logout'),
    path('teacherlogin', LoginView.as_view(template_name='accounts/teacherlogin.html'), name='teacherlogin'),
    path('teachersregister', views.teachersregister, name='teachersregister'),
    path('teacher_logout', views.teacher_logout_view, name='teacher_logout'),
]