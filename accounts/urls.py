from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView    

urlpatterns = [
    path('studentlogin', LoginView.as_view(template_name='accounts/studentlogin.html'), name='studentlogin'),
    path('studentregister', views.studentregister, name='studentregister'),
]