from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import *
from accounts.forms import *
from coursework.models import Enrollment, Unit, Course, Cohort, EnrollmentRequest
from coursework.forms import CourseForm, CohortForm, UnitForm
from django.contrib import messages
from django.utils import timezone

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

        # Get the student's active enrollment
        enrollment = Enrollment.objects.filter(student=student, status='active').select_related('cohort__course').first()
        enrolled_cohort = enrollment.cohort if enrollment else None
        enrolled_course = enrolled_cohort.course if enrolled_cohort else None
        cohort_units = enrolled_cohort.units.all() if enrolled_cohort else []

        # Get pending enrollment requests
        pending_requests = EnrollmentRequest.objects.filter(
            student=student,
            status='pending'
        ).select_related('cohort__course')

        # Get available cohorts (excluding those the student is already enrolled in or has pending requests for)
        enrolled_cohort_ids = Enrollment.objects.filter(student=student).values_list('cohort_id', flat=True)
        requested_cohort_ids = EnrollmentRequest.objects.filter(student=student).values_list('cohort_id', flat=True)
        available_cohorts = Cohort.objects.exclude(
            cohort_id__in=list(enrolled_cohort_ids) + list(requested_cohort_ids)
        ).select_related('course')

    except Student.DoesNotExist:
        return redirect('studentregister')

    context = {
        'student': student,
        'student_profile': student_profile,
        'enrolled_cohort': enrolled_cohort,
        'enrolled_course': enrolled_course,
        'cohort_units': cohort_units,
        'pending_requests': pending_requests,
        'available_cohorts': available_cohorts,
    }
    return render(request, 'dashboard/students/student_dashboard.html', context)

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
            student_profile = StudentProfile(student=student)
            form = StudentProfileForm(request.POST, request.FILES, instance=student_profile)
        if form.is_valid():
            student_profile = form.save(commit=False)
            student_profile.student = student
            student_profile.save()
            return redirect('student_dashboard')
        else:
            pass
    else:
        try:
            student_profile = StudentProfile.objects.get(student=student)
            form = StudentProfileForm(instance=student_profile)
        except StudentProfile.DoesNotExist:
            student_profile = StudentProfile(student=student)
            form = StudentProfileForm(instance=student_profile)
    return render(request, 'dashboard/students/update_student_profile.html', {'form': form})

@login_required
def request_enrollment(request, cohort_id):
    try:
        student = Student.objects.get(user=request.user)
        cohort = get_object_or_404(Cohort, cohort_id=cohort_id)
        
        # Check if student already has an active enrollment or pending request
        existing_enrollment = Enrollment.objects.filter(student=student, cohort=cohort).exists()
        existing_request = EnrollmentRequest.objects.filter(student=student, cohort=cohort).exists()
        
        if existing_enrollment or existing_request:
            messages.error(request, 'You already have an active enrollment or pending request for this cohort.')
            return redirect('student_dashboard')
            
        if request.method == 'POST':
            notes = request.POST.get('notes', '')
            EnrollmentRequest.objects.create(
                student=student,
                cohort=cohort,
                notes=notes
            )
            messages.success(request, 'Enrollment request submitted successfully!')
            return redirect('student_dashboard')
            
        return render(request, 'dashboard/students/request_enrollment.html', {
            'cohort': cohort,
            'student': student
        })
        
    except Student.DoesNotExist:
        return redirect('studentregister')

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
    return render(request, 'dashboard/teachers/teacher_dashboard.html', context)


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
    return render(request, 'dashboard/teachers/update_teacher_profile.html', {'form': form})

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
    return render(request, 'dashboard/teachers/teacher_courses.html', context)

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
    return render(request, 'dashboard/teachers/add_course.html', context)

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
    
    return render(request, 'dashboard/teachers/edit_course.html', {
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
    
    return render(request, 'dashboard/teachers/edit_cohort.html', {
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
    
    return render(request, 'dashboard/teachers/edit_unit.html', {
        'form': form,
        'teacher': request.user.teacher,
        'teacher_profile': request.user.teacher.teacherprofile
    })

@login_required
def manage_enrollment_requests(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
        
        # Get all enrollment requests for cohorts that this teacher teaches
        teacher_cohorts = Cohort.objects.filter(units__teacher=teacher).distinct()
        enrollment_requests = EnrollmentRequest.objects.filter(
            cohort__in=teacher_cohorts,
            status='pending'
        ).select_related(
            'student',
            'student__user',
            'cohort',
            'cohort__course'
        ).order_by('-requested_at')
        
        if request.method == 'POST':
            request_id = request.POST.get('request_id')
            action = request.POST.get('action')
            notes = request.POST.get('notes', '')
            
            try:
                enrollment_request = EnrollmentRequest.objects.get(
                    id=request_id,
                    cohort__in=teacher_cohorts,
                    status='pending'
                )
                
                if action == 'approve':
                    # Create enrollment
                    Enrollment.objects.create(
                        student=enrollment_request.student,
                        cohort=enrollment_request.cohort,
                        status='active'
                    )
                    enrollment_request.status = 'approved'
                    messages.success(request, 'Enrollment request approved successfully!')
                    
                elif action == 'reject':
                    enrollment_request.status = 'rejected'
                    messages.success(request, 'Enrollment request rejected successfully!')
                
                enrollment_request.notes = notes
                enrollment_request.reviewed_by = teacher
                enrollment_request.reviewed_at = timezone.now()
                enrollment_request.save()
                
            except EnrollmentRequest.DoesNotExist:
                messages.error(request, 'Enrollment request not found!')
                
            return redirect('manage_enrollment_requests')
            
    except Teacher.DoesNotExist:
        return redirect('teachersregister')
        
    context = {
        'teacher': teacher,
        'enrollment_requests': enrollment_requests
    }
    return render(request, 'dashboard/teachers/manage_enrollment_requests.html', context)