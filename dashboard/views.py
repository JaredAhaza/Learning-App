from django.shortcuts import render

# Create your views here.
def student_dashboard(request):
    return render(request, 'dashboard/student_dashboard.html')

def update_student_profile(request):
    return render(request, 'dashboard/update_student_profile.html')

def student_profile(request):
    return render(request, 'dashboard/student_profile.html')