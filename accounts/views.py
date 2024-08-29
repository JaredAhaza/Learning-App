from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.models import Group
from .forms import StudentUserForm, StudentForm
from .models import Student  # Import Student from your app's models

def student_signup_view(request):
    userForm = StudentUserForm()
    StudentForm = StudentForm()
    mydict = {'userForm': userForm, 'StudentForm': StudentForm}
    if request.method == 'POST':
        userForm = StudentUserForm(request.POST)
        StudentForm = StudentForm(request.POST, request.FILES)
        if userForm.is_valid() and StudentForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            student = StudentForm.save(commit=False)
            student.user = user
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
        return HttpResponseRedirect('studentlogin')
    return render(request, 'student/student_signup.html', context=mydict)


def is_student(user):
    return user.groups.filter(name='STUDENT').exists()