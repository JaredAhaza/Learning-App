from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
from accounts.models import StudentProfile
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.models import Student, Teacher, TeacherProfile
from django.db.models import Q

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

@login_required
def create_quiz(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if hasattr(lesson, 'quiz'):
        return redirect('edit_quiz', quiz_id=lesson.quiz.id)
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.lesson = lesson
            quiz.save()
            messages.success(request, 'Quiz created!')
            return redirect('edit_quiz', quiz_id=quiz.id)
    else:
        form = QuizForm()
    return render(request, 'coursework/quiz_form.html', {'form': form, 'lesson': lesson})

@login_required
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz updated!')
            return redirect('edit_quiz', quiz_id=quiz.id)
    else:
        form = QuizForm(instance=quiz)
    questions = quiz.questions.all()
    return render(request, 'coursework/quiz_edit.html', {'form': form, 'quiz': quiz, 'questions': questions})

@login_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'Question added!')
            return redirect('edit_quiz', quiz_id=quiz.id)
    else:
        form = QuestionForm()
    return render(request, 'coursework/question_form.html', {'form': form, 'quiz': quiz})

@login_required
def add_answer(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.save()
            messages.success(request, 'Answer added!')
            return redirect('edit_quiz', quiz_id=question.quiz.id)
    else:
        form = AnswerForm()
    return render(request, 'coursework/answer_form.html', {'form': form, 'question': question})

@login_required
def take_quiz(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    quiz = get_object_or_404(Quiz, lesson=lesson)
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    if request.method == 'POST':
        submission = StudentQuizSubmission.objects.create(student=student_profile, quiz=quiz)
        for question in quiz.questions.all():
            q_key = f'question_{question.id}'
            if question.question_type in ['MCQ', 'YESNO']:
                answer_id = request.POST.get(q_key)
                StudentAnswer.objects.create(submission=submission, question=question, selected_answer_id=answer_id)
            else:
                text = request.POST.get(q_key)
                StudentAnswer.objects.create(submission=submission, question=question, text_answer=text)
        submission.auto_mark()
        messages.success(request, 'Quiz submitted!')
        return redirect('quiz_result', submission_id=submission.id)
    return render(request, 'coursework/take_quiz.html', {'quiz': quiz, 'lesson': lesson})

@login_required
def quiz_result(request, submission_id):
    submission = get_object_or_404(StudentQuizSubmission, id=submission_id)
    return render(request, 'coursework/quiz_result.html', {'submission': submission})

@login_required
def review_explanatory_answers(request):
    submissions = StudentQuizSubmission.objects.filter(quiz__questions__question_type='EXPLAIN', reviewed=False).distinct()
    return render(request, 'coursework/review_explanatory_list.html', {'submissions': submissions})

@login_required
def review_explanatory_detail(request, submission_id):
    submission = get_object_or_404(StudentQuizSubmission, id=submission_id)
    if request.method == 'POST':
        feedback = request.POST.get('feedback')
        score = request.POST.get('score')
        submission.feedback = feedback
        submission.score = score
        submission.reviewed = True
        submission.save()
        messages.success(request, 'Submission reviewed!')
        return redirect('review_explanatory_answers')
    return render(request, 'coursework/review_explanatory_detail.html', {'submission': submission})

@login_required
def create_project(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.lesson = lesson
            project.save()
            messages.success(request, 'Project created!')
            return redirect('lesson_view', lesson_id=lesson.id)
    else:
        form = ProjectForm()
    return render(request, 'coursework/project_form.html', {'form': form, 'lesson': lesson})

@login_required
def submit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    if request.method == 'POST':
        form = ProjectSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.project = project
            submission.student = student_profile
            submission.save()
            messages.success(request, 'Project submitted!')
            return redirect('project_result', submission_id=submission.id)
    else:
        form = ProjectSubmissionForm()
    return render(request, 'coursework/submit_project.html', {'form': form, 'project': project})

@login_required
def review_projects(request):
    projects = ProjectSubmission.objects.filter(reviewed=False)
    return render(request, 'coursework/review_project_list.html', {'projects': projects})

@login_required
def review_project_detail(request, submission_id):
    submission = get_object_or_404(ProjectSubmission, id=submission_id)
    if request.method == 'POST':
        feedback = request.POST.get('feedback')
        grade = request.POST.get('grade')
        submission.feedback = feedback
        submission.grade = grade
        submission.reviewed = True
        submission.save()
        messages.success(request, 'Project reviewed!')
        return redirect('review_projects')
    return render(request, 'coursework/review_project_detail.html', {'submission': submission})

@login_required
def project_result(request, submission_id):
    submission = get_object_or_404(ProjectSubmission, id=submission_id)
    return render(request, 'coursework/project_result.html', {'submission': submission})

# Timetable views (moved from timetable.py)
@login_required
def teacher_timetable(request):
    try:
        teacher = request.user.teacher
        try:
            teacher_profile = TeacherProfile.objects.get(teacher=teacher)
        except TeacherProfile.DoesNotExist:
            teacher_profile = None
        current_date = timezone.now().date()
        start_of_week = current_date - timedelta(days=current_date.weekday())
        end_of_week = start_of_week + timedelta(days=4)
        lessons = Lesson.objects.filter(teacher=teacher)
        time_slots = TimeSlot.objects.filter(
            teacher=teacher,
            lesson__in=lessons
        ).select_related('lesson', 'lesson__unit')
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
    try:
        student = request.user.student
        try:
            student_profile = StudentProfile.objects.get(student=student)
        except StudentProfile.DoesNotExist:
            student_profile = None
        enrollment = Enrollment.objects.filter(student=student, status='active').select_related('cohort__course').first()
        enrolled_cohort = enrollment.cohort if enrollment else None
        enrolled_course = enrolled_cohort.course if enrolled_cohort else None
        enrollments = student.enrollment_set.filter(status='active').select_related('cohort', 'cohort__course')
        units = [enrollment.cohort.units.all() for enrollment in enrollments]
        units = [unit for sublist in units for unit in sublist]
        lessons = Lesson.objects.filter(unit__in=units)
        time_slots = TimeSlot.objects.filter(
            lesson__in=lessons
        ).select_related('lesson', 'lesson__unit', 'teacher')
        today = timezone.now().strftime('%a').upper()[:3]
        today_schedule = time_slots.filter(day=today).order_by('start_time')
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
    if lesson.unit.teacher != teacher:
        messages.error(request, "You can only add time slots for lessons in units assigned to you.")
        return redirect('teacher_dashboard')
    if request.method == 'POST':
        day = request.POST.get('day')
        start_time = request.POST.get('start_time')
        if TimeSlot.objects.filter(
            teacher=teacher,
            day=day,
            start_time=start_time,
            is_booked=True
        ).exists():
            messages.error(request, "This time slot is already booked.")
            return redirect('teacher_dashboard')
        time_slot = TimeSlot.objects.create(
            day=day,
            start_time=start_time,
            lesson=lesson,
            teacher=teacher,
            is_booked=True
        )
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
