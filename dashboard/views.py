from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def student_dashboard(request):
    return render(request, 'dashboard/student_dashboard.html')

@login_required
def update_student_profile(request):
    return render(request, 'dashboard/update_student_profile.html')
