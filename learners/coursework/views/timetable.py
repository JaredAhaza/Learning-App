from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from ..models import TimeSlot, Lesson, StudentProfile, Enrollment
from accounts.models import Student, Teacher, TeacherProfile
from django.db.models import Q

@login_required
def teacher_timetable(request):
    """View for teacher's timetable."""
    try:
        teacher = request.user.teacher
        try:
            teacher_profile = TeacherProfile.objects.get(teacher=teacher)
        except TeacherProfile.DoesNotExist:
            teacher_profile = None
            
        current_date = timezone.now().date()
        
        # Get all time slots for the current week
        start_of_week = current_date - timedelta(days=current_date.weekday())
        end_of_week = start_of_week + timedelta(days=4)  # Friday
        
        # Get all lessons for the teacher
        lessons = Lesson.objects.filter(teacher=teacher)
        
        # Get all time slots for the teacher's lessons
        time_slots = TimeSlot.objects.filter(
            teacher=teacher,
            lesson__in=lessons
        ).select_related('lesson', 'lesson__unit')
        
        # Organize time slots by day and time
        schedule = {}
        for day, _ in TimeSlot.DAYS_OF_WEEK:
            schedule[day] = {}
            for time, _ in TimeSlot.TIME_SLOTS:
                schedule[day][time] = None
        
        for slot in time_slots:
            schedule[slot.day][slot.start_time] = slot
        
        context = {
            'teacher': teacher,
            'teacher_profile': teacher_profile,
            'days_of_week': TimeSlot.DAYS_OF_WEEK,
            'time_slots': TimeSlot.TIME_SLOTS,
            'schedule': schedule,
            'current_week': f"Week of {start_of_week.strftime('%B %d, %Y')}",
        }
        
        return render(request, 'dashboard/teachers/teacher_dashboard.html', context)
        
    except Teacher.DoesNotExist:
        return redirect('teachersregister')

@login_required
def student_timetable(request):
    """View for student's timetable."""
    try:
        student = request.user.student
        try:
            student_profile = StudentProfile.objects.get(student=student)
        except StudentProfile.DoesNotExist:
            student_profile = None

        # Get the student's active enrollment
        enrollment = Enrollment.objects.filter(student=student, status='active').select_related('cohort__course').first()
        enrolled_cohort = enrollment.cohort if enrollment else None
        enrolled_course = enrolled_cohort.course if enrolled_cohort else None
        
        # Get all enrollments for the student
        enrollments = student.enrollment_set.filter(status='active').select_related(
            'cohort', 'cohort__course'
        )
        
        # Get all units from the student's active enrollments
        units = [enrollment.cohort.units.all() for enrollment in enrollments]
        units = [unit for sublist in units for unit in sublist]
        
        # Get all lessons from the student's units
        lessons = Lesson.objects.filter(unit__in=units)
        
        # Get all time slots for these lessons
        time_slots = TimeSlot.objects.filter(
            lesson__in=lessons
        ).select_related('lesson', 'lesson__unit', 'teacher')
        
        # Get today's schedule
        today = timezone.now().strftime('%a').upper()[:3]
        today_schedule = time_slots.filter(day=today).order_by('start_time')
        
        # Organize time slots by day and time
        schedule = {}
        for day, _ in TimeSlot.DAYS_OF_WEEK:
            schedule[day] = {}
            for time, _ in TimeSlot.TIME_SLOTS:
                schedule[day][time] = None
        
        for slot in time_slots:
            schedule[slot.day][slot.start_time] = slot
        
        context = {
            'student': student,
            'student_profile': student_profile,
            'enrolled_cohort': enrolled_cohort,
            'enrolled_course': enrolled_course,
            'days_of_week': TimeSlot.DAYS_OF_WEEK,
            'time_slots': TimeSlot.TIME_SLOTS,
            'schedule': schedule,
            'today_schedule': today_schedule,
            'current_week': f"Week of {timezone.now().date().strftime('%B %d, %Y')}",
        }
        
        return render(request, 'dashboard/students/student_dashboard.html', context)
        
    except Student.DoesNotExist:
        return redirect('studentregister')

@login_required
def add_time_slot(request, lesson_id):
    """View to add a time slot for a lesson."""
    try:
        teacher = request.user.teacher
        try:
            teacher_profile = TeacherProfile.objects.get(teacher=teacher)
        except TeacherProfile.DoesNotExist:
            teacher_profile = None
    except:
        messages.error(request, "Only teachers can add time slots.")
        return redirect('student_dashboard')
    
    lesson = Lesson.objects.get(id=lesson_id)
    
    # Check if the teacher is assigned to this lesson's unit
    if lesson.unit.teacher != teacher:
        messages.error(request, "You can only add time slots for lessons in units assigned to you.")
        return redirect('teacher_dashboard')
    
    if request.method == 'POST':
        day = request.POST.get('day')
        start_time = request.POST.get('start_time')
        
        # Check if the time slot is already booked for this teacher
        if TimeSlot.objects.filter(
            teacher=teacher,
            day=day,
            start_time=start_time,
            is_booked=True
        ).exists():
            messages.error(request, "This time slot is already booked.")
            return redirect('teacher_dashboard')
        
        # Create the time slot with automatic teacher assignment
        time_slot = TimeSlot.objects.create(
            day=day,
            start_time=start_time,
            lesson=lesson,
            teacher=teacher,  # Automatically assign the teacher from the lesson's unit
            is_booked=True
        )
        
        # The end_time will be automatically calculated in the save method
        
        messages.success(request, f"Time slot added successfully. Duration: {lesson.get_formatted_duration()}")
        return redirect('teacher_dashboard')
    
    context = {
        'teacher': teacher,
        'teacher_profile': teacher_profile,
        'lesson': lesson,
        'days_of_week': TimeSlot.DAYS_OF_WEEK,
        'time_slots': TimeSlot.TIME_SLOTS,
    }
    
    return render(request, 'coursework/add_time_slot.html', context)

@login_required
def remove_time_slot(request, time_slot_id):
    """View to remove a time slot."""
    try:
        teacher = request.user.teacher
    except:
        messages.error(request, "Only teachers can remove time slots.")
        return redirect('student_dashboard')
    
    time_slot = TimeSlot.objects.get(id=time_slot_id)
    
    if time_slot.teacher != teacher:
        messages.error(request, "You can only remove your own time slots.")
        return redirect('teacher_dashboard')
    
    time_slot.delete()
    messages.success(request, "Time slot removed successfully.")
    return redirect('teacher_dashboard') 