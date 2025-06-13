from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import *
from accounts.forms import *
from coursework.models import Enrollment, Unit, Course, Cohort
from coursework.forms import CourseForm, CohortForm, UnitForm
from django.contrib import messages

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
        # Get the student's active enrollment (assuming one active at a time)
        enrollment = Enrollment.objects.filter(student=student, status='active').select_related('cohort__course').first()
        enrolled_cohort = enrollment.cohort if enrollment else None
        enrolled_course = enrolled_cohort.course if enrolled_cohort else None
        cohort_units = enrolled_cohort.units.all() if enrolled_cohort else []
    except Student.DoesNotExist:
        return redirect ('studentregister')
    context = {
        'student': student,
        'student_profile': student_profile,
        'enrolled_cohort': enrolled_cohort,
        'enrolled_course': enrolled_course,
        'cohort_units': cohort_units,
    }
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
            
        # Get all units assigned to this teacher with related data
        assigned_units = Unit.objects.filter(teacher=teacher).select_related('cohort', 'cohort__course')
        
        # Get all enrollments for the cohorts of the teacher's units
        all_enrollments = []
        for unit in assigned_units:
            enrollments = Enrollment.objects.filter(
                cohort=unit.cohort,
                status='active'
            ).select_related(
                'student',
                'student__user',
                'cohort',
                'cohort__course'
            )
            for enrollment in enrollments:
                all_enrollments.append({
                    'student_name': enrollment.student.user.get_full_name(),
                    'student_id': enrollment.student.student_id,
                    'unit_name': unit.unit_name,
                    'cohort_name': unit.cohort.name,
                    'course_name': unit.cohort.course.course_name,
                    'status': enrollment.status
                })
    except Teacher.DoesNotExist:
        return redirect('teachersregister')
        
    context = {
        'teacher': teacher, 
        'teacher_profile': teacher_profile,
        'assigned_units': assigned_units,
        'all_enrollments': all_enrollments
    }
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

@login_required
def teacher_courses(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
        try:
            teacher_profile = TeacherProfile.objects.get(teacher=teacher)
        except TeacherProfile.DoesNotExist:
            teacher_profile = None
            
        # Get all units assigned to this teacher with related data
        assigned_units = Unit.objects.filter(teacher=teacher).select_related(
            'cohort',
            'cohort__course'
        ).order_by('cohort__course__course_name', 'cohort__name', 'unit_name')
        
        # Organize data by course
        courses_data = {}
        for unit in assigned_units:
            course = unit.cohort.course
            cohort = unit.cohort
            
            if course.course_id not in courses_data:
                courses_data[course.course_id] = {
                    'course': course,
                    'cohorts': {}
                }
            
            if cohort.cohort_id not in courses_data[course.course_id]['cohorts']:
                courses_data[course.course_id]['cohorts'][cohort.cohort_id] = {
                    'cohort': cohort,
                    'units': []
                }
            
            courses_data[course.course_id]['cohorts'][cohort.cohort_id]['units'].append(unit)
            
    except Teacher.DoesNotExist:
        return redirect('teachersregister')
        
    context = {
        'teacher': teacher,
        'teacher_profile': teacher_profile,
        'courses_data': courses_data
    }
    return render(request, 'dashboard/teacher_courses.html', context)

@login_required
def add_course(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
        try:
            teacher_profile = TeacherProfile.objects.get(teacher=teacher)
        except TeacherProfile.DoesNotExist:
            teacher_profile = None
            
        if request.method == 'POST':
            form_type = request.POST.get('form_type')
            
            if form_type == 'course':
                form = CourseForm(request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Course added successfully!')
                    return redirect('add_course')
                    
            elif form_type == 'cohort':
                form = CohortForm(request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Cohort added successfully!')
                    return redirect('add_course')
                    
            elif form_type == 'unit':
                form = UnitForm(request.POST)
                if form.is_valid():
                    unit = form.save(commit=False)
                    unit.teacher = teacher
                    unit.save()
                    messages.success(request, 'Unit added successfully!')
                    return redirect('add_course')
        else:
            course_form = CourseForm()
            cohort_form = CohortForm()
            unit_form = UnitForm()
            
        # Get existing courses and cohorts for the select dropdowns
        courses = Course.objects.all()
        cohorts = Cohort.objects.all()
            
    except Teacher.DoesNotExist:
        return redirect('teachersregister')
        
    context = {
        'teacher': teacher,
        'teacher_profile': teacher_profile,
        'course_form': course_form,
        'cohort_form': cohort_form,
        'unit_form': unit_form,
        'courses': courses,
        'cohorts': cohorts
    }
    return render(request, 'dashboard/add_course.html', context)

@login_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, course_id=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('teacher_courses')
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'dashboard/edit_course.html', {
        'form': form,
        'teacher': request.user.teacher,
        'teacher_profile': request.user.teacher.teacherprofile
    })

@login_required
def edit_cohort(request, cohort_id):
    cohort = get_object_or_404(Cohort, cohort_id=cohort_id)
    existing_units = Unit.objects.filter(cohort=cohort)
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'cohort':
            form = CohortForm(request.POST, instance=cohort)
            if form.is_valid():
                form.save()
                messages.success(request, 'Cohort updated successfully!')
                return redirect('teacher_courses')
                
        elif form_type == 'add_unit':
            unit_form = UnitForm(request.POST)
            if unit_form.is_valid():
                unit = unit_form.save(commit=False)
                unit.cohort = cohort
                unit.teacher = request.user.teacher
                unit.save()
                messages.success(request, 'Unit added successfully!')
                return redirect('edit_cohort', cohort_id=cohort_id)
                
        elif form_type == 'remove_unit':
            unit_id = request.POST.get('unit_id')
            try:
                unit = Unit.objects.get(unit_id=unit_id, cohort=cohort)
                unit.delete()
                messages.success(request, 'Unit removed successfully!')
            except Unit.DoesNotExist:
                messages.error(request, 'Unit not found!')
            return redirect('edit_cohort', cohort_id=cohort_id)
    else:
        form = CohortForm(instance=cohort)
        unit_form = UnitForm(initial={'cohort': cohort})
    
    return render(request, 'dashboard/edit_cohort.html', {
        'form': form,
        'unit_form': unit_form,
        'existing_units': existing_units,
        'teacher': request.user.teacher,
        'teacher_profile': request.user.teacher.teacherprofile
    })

@login_required
def edit_unit(request, unit_id):
    unit = get_object_or_404(Unit, unit_id=unit_id)
    if request.method == 'POST':
        form = UnitForm(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Unit updated successfully!')
            return redirect('teacher_courses')
    else:
        form = UnitForm(instance=unit)
    
    return render(request, 'dashboard/edit_unit.html', {
        'form': form,
        'teacher': request.user.teacher,
        'teacher_profile': request.user.teacher.teacherprofile
    })