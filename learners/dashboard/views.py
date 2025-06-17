from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import *
from accounts.forms import *
from coursework.models import Enrollment, Unit, Course, Cohort, EnrollmentRequest, LessonProgress, Lesson, TopicProgress, OnlineClass, TimeSlot
from coursework.forms import CourseForm, CohortForm, UnitForm, OnlineClassForm
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta

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
        
        # Get completed enrollments for notification
        completed_enrollments = Enrollment.objects.filter(
            student=student,
            status='completed'
        ).select_related('cohort__course').order_by('-enrolled_at')
        
        # Get units with progress
        cohort_units = []
        if enrolled_cohort:
            units = enrolled_cohort.units.all()
            for unit in units:
                # Calculate unit progress
                total_lessons = unit.lessons.count()
                completed_lessons = LessonProgress.objects.filter(
                    student=student,
                    lesson__unit=unit,
                    completed=True
                ).count()
                
                progress_percentage = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
                
                cohort_units.append({
                    'unit': unit,
                    'progress': progress_percentage,
                    'completed_lessons': completed_lessons,
                    'total_lessons': total_lessons
                })

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

        # Get timetable data
        current_date = timezone.now().date()
        start_of_week = current_date - timedelta(days=current_date.weekday())
        
        # Get all enrollments for the student
        enrollments = student.enrollment_set.filter(status='active').select_related(
            'cohort', 'cohort__course'
        )
        
        # Get all units from the student's active enrollments
        units = []
        for enrollment in enrollments:
            units.extend(enrollment.cohort.units.all())
        
        # Get all lessons from the student's units
        lessons = Lesson.objects.filter(unit__in=units)
        
        # Get all time slots for these lessons
        time_slots = TimeSlot.objects.filter(
            lesson__in=lessons
        ).select_related('lesson', 'lesson__unit', 'teacher')
        
        # Get all online classes for these units
        online_classes = OnlineClass.objects.filter(
            unit__in=units
        ).select_related('unit')
        
        # Get today's schedule
        today = timezone.now().strftime('%a').upper()[:3]
        today_schedule = time_slots.filter(day=today).order_by('start_time')
        
        # Add today's online classes to today's schedule
        today_online_classes = online_classes.filter(
            start_time__date=timezone.now().date()
        ).order_by('start_time')
        
        # Convert online classes to today's schedule format
        for online_class in today_online_classes:
            class_slot = online_class.to_timetable_slot()
            if class_slot:
                # Create a mock slot for today's schedule
                today_slot = type('MockTodaySlot', (), {
                    'get_start_time_display': lambda: class_slot.start_time,
                    'lesson': class_slot.lesson
                })()
                today_schedule = list(today_schedule) + [today_slot]
        
        # Organize time slots by day and time
        schedule = {}
        for day, _ in TimeSlot.DAYS_OF_WEEK:
            schedule[day] = {}
            for time, _ in TimeSlot.TIME_SLOTS:
                schedule[day][time] = None
        
        # Add TimeSlot data
        for slot in time_slots:
            schedule[slot.day][slot.start_time] = slot
        
        # Add OnlineClass data to schedule
        for online_class in online_classes:
            class_slot = online_class.to_timetable_slot()
            if class_slot and class_slot.day in schedule and class_slot.start_time in schedule[class_slot.day]:
                schedule[class_slot.day][class_slot.start_time] = class_slot

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
        'completed_enrollments': completed_enrollments,
        'days_of_week': TimeSlot.DAYS_OF_WEEK,
        'time_slots': TimeSlot.TIME_SLOTS,
        'schedule': schedule,
        'today_schedule': today_schedule,
        'current_week': f"Week of {start_of_week.strftime('%B %d, %Y')}",
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
            
        # Handle POST requests for enrollment request actions
        if request.method == 'POST':
            request_id = request.POST.get('request_id')
            action = request.POST.get('action')
            notes = request.POST.get('notes', '')
            
            if request_id and action:
                # Get teacher's cohorts to verify access
                teacher_cohorts = Cohort.objects.filter(units__teacher=teacher).distinct()
                
                try:
                    enrollment_request = EnrollmentRequest.objects.get(
                        id=request_id,
                        cohort__in=teacher_cohorts,
                        status='pending'
                    )
                    
                    if action == 'approve':
                        # Get student's current active enrollment
                        current_enrollment = Enrollment.objects.filter(
                            student=enrollment_request.student,
                            status='active'
                        ).first()
                        
                        if current_enrollment:
                            # Update status of current enrollment to 'completed'
                            current_enrollment.status = 'completed'
                            current_enrollment.save()
                        
                        # Create new enrollment
                        new_enrollment = Enrollment.objects.create(
                            student=enrollment_request.student,
                            cohort=enrollment_request.cohort,
                            status='active'
                        )
                        
                        # Update enrollment request status
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
                
                return redirect('teacher_dashboard')
            
        # Get all units assigned to this teacher with related data
        assigned_units = Unit.objects.filter(teacher=teacher).select_related('cohort', 'cohort__course').prefetch_related('lessons')
        
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
        
        # Get enrollment requests for the teacher's cohorts (limited to 3 most recent)
        teacher_cohorts = Cohort.objects.filter(units__teacher=teacher).distinct()
        enrollment_requests = EnrollmentRequest.objects.filter(
            cohort__in=teacher_cohorts,
            status='pending'
        ).select_related(
            'student',
            'student__user',
            'cohort',
            'cohort__course'
        ).order_by('-requested_at')[:3]
        
        # Get timetable data
        current_date = timezone.now().date()
        start_of_week = current_date - timedelta(days=current_date.weekday())
        
        # Get all lessons for the teacher
        lessons = Lesson.objects.filter(teacher=teacher)
        
        # Get all time slots for the teacher's lessons
        time_slots = TimeSlot.objects.filter(
            teacher=teacher,
            lesson__in=lessons
        ).select_related('lesson', 'lesson__unit')
        
        # Get all online classes for the teacher's units
        online_classes = OnlineClass.objects.filter(
            unit__teacher=teacher
        ).select_related('unit')
        
        # Organize time slots by day and time
        schedule = {}
        for day, _ in TimeSlot.DAYS_OF_WEEK:
            schedule[day] = {}
            for time, _ in TimeSlot.TIME_SLOTS:
                schedule[day][time] = None
        
        # Add TimeSlot data
        for slot in time_slots:
            schedule[slot.day][slot.start_time] = slot
        
        # Add OnlineClass data to schedule
        for online_class in online_classes:
            class_slot = online_class.to_timetable_slot()
            if class_slot and class_slot.day in schedule and class_slot.start_time in schedule[class_slot.day]:
                schedule[class_slot.day][class_slot.start_time] = class_slot

    except Teacher.DoesNotExist:
        return redirect('teachersregister')
        
    context = {
        'teacher': teacher, 
        'teacher_profile': teacher_profile,
        'assigned_units': assigned_units,
        'all_enrollments': all_enrollments,
        'enrollment_requests': enrollment_requests,
        'days_of_week': TimeSlot.DAYS_OF_WEEK,
        'time_slots': TimeSlot.TIME_SLOTS,
        'schedule': schedule,
        'current_week': f"Week of {start_of_week.strftime('%B %d, %Y')}",
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
        ).prefetch_related(
            'lessons'
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
            
            # Get lessons for this unit
            unit_with_lessons = {
                'unit': unit,
                'lessons': unit.lessons.all()
            }
            courses_data[course.course_id]['cohorts'][cohort.cohort_id]['units'].append(unit_with_lessons)
            
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
                    # Get student's current active enrollment
                    current_enrollment = Enrollment.objects.filter(
                        student=enrollment_request.student,
                        status='active'
                    ).first()
                    
                    if current_enrollment:
                        # Update status of current enrollment to 'completed'
                        current_enrollment.status = 'completed'
                        current_enrollment.save()
                        
                        # Add a one-time message for the student about cohort change
                        messages.info(
                            request, 
                            f'You have been moved from {current_enrollment.cohort.name} to {enrollment_request.cohort.name}. Your progress has been preserved.',
                            extra_tags='cohort_change'
                        )
                    
                    # Create new enrollment
                    new_enrollment = Enrollment.objects.create(
                        student=enrollment_request.student,
                        cohort=enrollment_request.cohort,
                        status='active'
                    )
                    
                    # Update enrollment request status
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

@login_required
def unit_lessons(request, unit_id):
    """View for managing lessons within a unit."""
    if request.user.groups.filter(name='TEACHER').exists():
        try:
            teacher = Teacher.objects.get(user=request.user)
            try:
                teacher_profile = TeacherProfile.objects.get(teacher=teacher)
            except TeacherProfile.DoesNotExist:
                teacher_profile = None
                
            unit = get_object_or_404(Unit, unit_id=unit_id)
            
            # Check if the teacher is assigned to this unit
            if unit.teacher != teacher:
                messages.error(request, "You are not assigned to this unit.")
                return redirect('teacher_dashboard')
            
            lessons = Lesson.objects.filter(unit=unit).order_by('created_at')
            
            if request.method == 'POST':
                # Handle adding a new lesson
                title = request.POST.get('title')
                description = request.POST.get('description')
                content = request.POST.get('content')
                video_url = request.POST.get('video_url')
                estimated_completion_time = request.POST.get('estimated_completion_time')
                reading_materials = request.FILES.get('reading_materials')
                
                lesson = Lesson.objects.create(
                    unit=unit,
                    title=title,
                    description=description,
                    content=content,
                    video_url=video_url,
                    estimated_completion_time=estimated_completion_time,
                    reading_materials=reading_materials
                )
                
                messages.success(request, "Lesson added successfully!")
                return redirect('unit_lessons', unit_id=unit_id)
            
            context = {
                'teacher': teacher,
                'teacher_profile': teacher_profile,
                'unit': unit,
                'lessons': lessons,
            }
            return render(request, 'dashboard/teachers/unit_lessons.html', context)
            
        except Teacher.DoesNotExist:
            return redirect('teachersregister')
        except Unit.DoesNotExist:
            messages.error(request, "Unit not found.")
            return redirect('teacher_dashboard')
    else:
        # Student view
        try:
            student = Student.objects.get(user=request.user)
            try:
                student_profile = StudentProfile.objects.get(student=student)
            except StudentProfile.DoesNotExist:
                student_profile = None
                
            unit = get_object_or_404(Unit, unit_id=unit_id)
            
            # Verify student is enrolled in the cohort that contains this unit
            enrollment = Enrollment.objects.filter(
                student=student,
                cohort=unit.cohort,
                status='active'
            ).first()
            
            if not enrollment:
                messages.error(request, 'You are not enrolled in this unit.')
                return redirect('student_dashboard')
                
            # Get all lessons for this unit
            lessons = unit.lessons.all().order_by('created_at')
            
            # Get progress for each lesson
            lesson_progress = []
            for lesson in lessons:
                progress = LessonProgress.objects.filter(
                    student=student,
                    lesson=lesson
                ).first()
                
                if not progress:
                    progress = LessonProgress.objects.create(
                        student=student,
                        lesson=lesson
                    )
                
                completion_percentage = lesson.get_completion_percentage(student)
                lesson_progress.append({
                    'lesson': lesson,
                    'progress': progress,
                    'completion_percentage': completion_percentage
                })
                
        except Student.DoesNotExist:
            return redirect('studentregister')
            
        context = {
            'student': student,
            'student_profile': student_profile,
            'unit': unit,
            'lesson_progress': lesson_progress
        }
        return render(request, 'dashboard/students/unit_lessons.html', context)

@login_required
def delete_lesson(request, lesson_id):
    """View for deleting a lesson."""
    if not request.user.groups.filter(name='TEACHER').exists():
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    try:
        teacher = Teacher.objects.get(user=request.user)
        lesson = Lesson.objects.get(id=lesson_id)
        # Check if the teacher is assigned to the unit
        if lesson.unit.teacher != teacher:
            return JsonResponse({'success': False, 'error': 'Permission denied'})
        
        lesson.delete()
        return JsonResponse({'success': True})
    except Teacher.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Teacher not found'})
    except Lesson.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Lesson not found'})

@login_required
def student_lesson_view(request, lesson_id):
    """View for students to access a specific lesson."""
    try:
        student = Student.objects.get(user=request.user)
        try:
            student_profile = StudentProfile.objects.get(student=student)
        except StudentProfile.DoesNotExist:
            student_profile = None
            
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        # Verify student is enrolled in the unit's cohort
        enrollment = Enrollment.objects.filter(
            student=student,
            cohort=lesson.unit.cohort,
            status='active'
        ).first()
        
        if not enrollment:
            messages.error(request, 'You are not enrolled in this lesson.')
            return redirect('student_dashboard')
            
        # Get or create lesson progress
        lesson_progress, created = LessonProgress.objects.get_or_create(
            student=student,
            lesson=lesson,
            defaults={'opened': True}
        )
        
        # Get topics for this lesson
        topics = lesson.topic_set.all()
        topic_progress = []
        for topic in topics:
            progress, created = TopicProgress.objects.get_or_create(
                student=student,
                topic=topic
            )
            topic_progress.append({
                'topic': topic,
                'progress': progress
            })
            
    except Student.DoesNotExist:
        return redirect('studentregister')
        
    context = {
        'student': student,
        'student_profile': student_profile,
        'lesson': lesson,
        'lesson_progress': lesson_progress,
        'topic_progress': topic_progress
    }
    return render(request, 'dashboard/students/lesson_view.html', context)

@login_required
def teacher_lesson_view(request, lesson_id):
    """View for teachers to view and manage a specific lesson."""
    try:
        teacher = Teacher.objects.get(user=request.user)
        try:
            teacher_profile = TeacherProfile.objects.get(teacher=teacher)
        except TeacherProfile.DoesNotExist:
            teacher_profile = None
            
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        # Verify teacher is assigned to this unit
        if lesson.unit.teacher != teacher:
            messages.error(request, 'You are not assigned to this lesson.')
            return redirect('teacher_dashboard')
            
        # Get all students enrolled in this lesson's cohort
        enrolled_students = Enrollment.objects.filter(
            cohort=lesson.unit.cohort,
            status='active'
        ).select_related('student', 'student__user')
        
        # Get progress for all students
        student_progress = []
        for enrollment in enrolled_students:
            progress = LessonProgress.objects.filter(
                student=enrollment.student,
                lesson=lesson
            ).first()
            
            if not progress:
                progress = LessonProgress.objects.create(
                    student=enrollment.student,
                    lesson=lesson
                )
                
            completion_percentage = lesson.get_completion_percentage(enrollment.student)
            student_progress.append({
                'student': enrollment.student,
                'progress': progress,
                'completion_percentage': completion_percentage
            })
            
    except Teacher.DoesNotExist:
        return redirect('teachersregister')
        
    context = {
        'teacher': teacher,
        'teacher_profile': teacher_profile,
        'lesson': lesson,
        'student_progress': student_progress
    }
    return render(request, 'dashboard/teachers/lesson_view.html', context)

@login_required
def complete_lesson(request, lesson_id):
    """View for marking a lesson as complete."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
        
    try:
        student = Student.objects.get(user=request.user)
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        # Verify student is enrolled in the unit's cohort
        enrollment = Enrollment.objects.filter(
            student=student,
            cohort=lesson.unit.cohort,
            status='active'
        ).first()
        
        if not enrollment:
            return JsonResponse({'success': False, 'error': 'You are not enrolled in this lesson.'})
            
        # Get or create lesson progress
        lesson_progress, created = LessonProgress.objects.get_or_create(
            student=student,
            lesson=lesson
        )
        
        # Mark lesson as complete
        lesson_progress.completed = True
        lesson_progress.save()
        
        # Mark all topics in this lesson as complete
        topics = lesson.topic_set.all()
        for topic in topics:
            topic_progress, created = TopicProgress.objects.get_or_create(
                student=student,
                topic=topic
            )
            topic_progress.completed = True
            topic_progress.save()
        
        # Calculate unit progress
        unit = lesson.unit
        total_lessons = unit.lessons.count()
        completed_lessons = LessonProgress.objects.filter(
            student=student,
            lesson__unit=unit,
            completed=True
        ).count()
        
        unit_progress = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
        
        return JsonResponse({
            'success': True,
            'unit_id': unit.unit_id,
            'unit_progress': unit_progress
        })
            
    except Student.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Student not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def unit_online_classes(request, unit_id):
    """View for managing online classes within a unit."""
    if request.user.groups.filter(name='TEACHER').exists():
        try:
            teacher = Teacher.objects.get(user=request.user)
            try:
                teacher_profile = TeacherProfile.objects.get(teacher=teacher)
            except TeacherProfile.DoesNotExist:
                teacher_profile = None
                
            unit = get_object_or_404(Unit, unit_id=unit_id)
            
            # Check if the teacher is assigned to this unit
            if unit.teacher != teacher:
                messages.error(request, "You are not assigned to this unit.")
                return redirect('teacher_dashboard')
            
            online_classes = OnlineClass.objects.filter(unit=unit).order_by('-start_time')
            
            if request.method == 'POST':
                form = OnlineClassForm(request.POST)
                if form.is_valid():
                    online_class = form.save(commit=False)
                    online_class.unit = unit
                    online_class.save()
                    messages.success(request, "Online class added successfully!")
                    return redirect('unit_online_classes', unit_id=unit_id)
            else:
                form = OnlineClassForm()
            
            context = {
                'teacher': teacher,
                'teacher_profile': teacher_profile,
                'unit': unit,
                'online_classes': online_classes,
                'form': form,
            }
            return render(request, 'dashboard/teachers/unit_online_classes.html', context)
            
        except Teacher.DoesNotExist:
            return redirect('teachersregister')
    else:
        # Student view
        try:
            student = Student.objects.get(user=request.user)
            try:
                student_profile = StudentProfile.objects.get(student=student)
            except StudentProfile.DoesNotExist:
                student_profile = None
                
            unit = get_object_or_404(Unit, unit_id=unit_id)
            
            # Verify student is enrolled in the cohort that contains this unit
            enrollment = Enrollment.objects.filter(
                student=student,
                cohort=unit.cohort,
                status='active'
            ).first()
            
            if not enrollment:
                messages.error(request, 'You are not enrolled in this unit.')
                return redirect('student_dashboard')
                
            # Get all online classes for this unit
            online_classes = unit.online_classes.all().order_by('-start_time')
            
        except Student.DoesNotExist:
            return redirect('studentregister')
            
        context = {
            'student': student,
            'student_profile': student_profile,
            'unit': unit,
            'online_classes': online_classes
        }
        return render(request, 'dashboard/students/unit_online_classes.html', context)

@login_required
def delete_online_class(request, class_id):
    """View for deleting an online class."""
    if not request.user.groups.filter(name='TEACHER').exists():
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    try:
        teacher = Teacher.objects.get(user=request.user)
        online_class = OnlineClass.objects.get(id=class_id)
        # Check if the teacher is assigned to the unit
        if online_class.unit.teacher != teacher:
            return JsonResponse({'success': False, 'error': 'Permission denied'})
        
        online_class.delete()
        return JsonResponse({'success': True})
    except Teacher.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Teacher not found'})
    except OnlineClass.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Online class not found'})