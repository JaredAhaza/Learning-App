from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import *
from accounts.forms import *

# Create your views here.
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