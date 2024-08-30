from django.shortcuts import render

# Create your views here.
def student_dashboard(request):
    return render(request, 'dashboard/student_dashboard.html')