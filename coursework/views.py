from django.shortcuts import render, redirect
from .forms import *
from .models import *

# Create your views here.
def add_course(request):
    print("add_course view called")
    if request.method == 'POST':
        print("Request method is POST")
        course_form = CourseForm(request.POST)
        print("Course form created")
        if course_form.is_valid():
            print("Course form is valid")
            course_form.save()
            print("Course saved")
            return redirect('course_list')
        else:
            print("Course form is not valid")
            print(course_form.errors)
    else:
        print("Request method is not POST")
        course_form = CourseForm()
    print("Rendering add_course.html")
    return render(request, 'coursework/add_course.html', {'course_form': course_form})