from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import *
from accounts.forms import *

# Create your views here.
@login_required
def redirect_to_dashboard(request):
    if request.user.groups.filter(name='STUDENT').exists():
        return redirect('student_dashboard')
    elif request.user.groups.filter(name='TEACHER').exists():
        return redirect('teacher_dashboard')
    else:
        return redirect('home')

@login_required
def student_dashboard(request):
    try:
        student = Student.objects.get(user=request.user)
        try:
            student_profile = StudentProfile.objects.get(student=student)
        except StudentProfile.DoesNotExist:
            student_profile = None
    except Student.DoesNotExist:
        return redirect ('studentregister')
    context = {'student': student, 'student_profile': student_profile}
    return render(request, 'dashboard/student_dashboard.html', context)

@login_required
def update_student_profile(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return redirect('studentregister')
    if request.method == 'POST':
        try:
            student_profile = StudentProfile.objects.get(student=student)
            form = StudentProfileForm(request.POST, request.FILES, instance=student_profile)
        except StudentProfile.DoesNotExist:
            student_profile = StudentProfile(student=student)  # Set the student field here
            form = StudentProfileForm(request.POST, request.FILES, instance=student_profile)
        if form.is_valid():
            student_profile = form.save(commit=False)  # Create a new StudentProfile instance
            student_profile.student = student  # Set the student field
            student_profile.save()
            return redirect('student_dashboard')
        else:
            pass
    else:
        try:
            student_profile = StudentProfile.objects.get(student=student)
            form = StudentProfileForm(instance=student_profile)
        except StudentProfile.DoesNotExist:
            student_profile = StudentProfile(student=student)  # Set the student field here
            form = StudentProfileForm(instance=student_profile)
    return render(request, 'dashboard/update_student_profile.html', {'form': form})


@login_required
def teacher_dashboard(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
        try:
            teacher_profile = TeacherProfile.objects.get(teacher=teacher)
        except TeacherProfile.DoesNotExist:
            teacher_profile = None
    except Teacher.DoesNotExist:
        return redirect ('teachersregister')
    context = {'teacher': teacher, 'teacher_profile': teacher_profile}
    return render(request, 'dashboard/teacher_dashboard.html', context)


@login_required
def update_teacher_profile(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        return redirect('teachersregister')
    if request.method == 'POST':
        try:
            teacher_profile = TeacherProfile.objects.get(teacher=teacher)
            form = TeacherProfileForm(request.POST, request.FILES, instance=teacher_profile)
        except TeacherProfile.DoesNotExist:
            teacher_profile = TeacherProfile(teacher=teacher)  # Set the teacher field here
            form = TeacherProfileForm(request.POST, request.FILES, instance=teacher_profile)
        if form.is_valid():
            teacher_profile = form.save(commit=False)  # Create a new TeacherProfile instance
            teacher_profile.teacher = teacher  # Set the student field
            teacher_profile.save()
            return redirect('teacher_dashboard')
        else:
            pass
    else:
        try:
            teacher_profile = TeacherProfile.objects.get(teacher=teacher)
            form = TeacherProfileForm(instance=teacher_profile)
        except TeacherProfile.DoesNotExist:
            teacher_profile = TeacherProfile(teacher=teacher)  # Set the teacher field here
            form = TeacherProfileForm(instance=teacher_profile)
    return render(request, 'dashboard/update_teacher_profile.html', {'form': form})