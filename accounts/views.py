from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.auth.models import Group
from django.contrib.auth import login, authenticate, logout
from .forms import *
from .models import *
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

def studentregister(request):
    if request.method == 'POST':
        user_form = StudentUserForm(request.POST)
        student_form = StudentForm(request.POST)
        
        if user_form.is_valid() and student_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password1'])
            user.save()
            
            student = student_form.save(commit=False)
            student.user = user
            student.save()
            group = Group.objects.get(name='STUDENT')
            user.groups.add(group)
            
            return redirect('studentlogin')
        else:
            pass
            # If forms are not valid, pass the forms with errors back to the template
            
    else:
        user_form = StudentUserForm()
        student_form = StudentForm()
        
    return render(request, 'accounts/studentregister.html', {'user_form': user_form, 'student_form': student_form})


# def studentlogin(request):
  #  return render(request, 'accounts/studentlogin.html')