from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from accounts.models import Student, StudentProfile, Teacher, TeacherProfile
from coursework.models import (
    Course, Cohort, Enrollment, TimeSlot, Lesson, Topic,
    Quiz, Question, Answer, Unit, OnlineClass
)
from django.utils import timezone
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populates the database with dummy data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing existing data...')
        
        # Clear existing data
        OnlineClass.objects.all().delete()
        Answer.objects.all().delete()
        Question.objects.all().delete()
        Quiz.objects.all().delete()
        Topic.objects.all().delete()
        Unit.objects.all().delete()
        Enrollment.objects.all().delete()
        Cohort.objects.all().delete()
        Course.objects.all().delete()
        StudentProfile.objects.all().delete()
        TeacherProfile.objects.all().delete()
        Student.objects.all().delete()
        Teacher.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()  # Keep superusers
        
        self.stdout.write('Creating dummy data...')

        # Create or get groups
        teacher_group, _ = Group.objects.get_or_create(name='TEACHER')
        student_group, _ = Group.objects.get_or_create(name='STUDENT')
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write('Created superuser')

        # Create teachers
        teachers = []
        for i in range(5):
            username = f'teacher{i}'
            email = f'teacher{i}@example.com'
            
            # Create user if it doesn't exist
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'password': 'teacher123'
                }
            )
            if created:
                user.set_password('teacher123')
                user.save()
            
            # Add user to teacher group
            user.groups.add(teacher_group)
            
            # Create teacher if it doesn't exist
            teacher, created = Teacher.objects.get_or_create(
                user=user,
                defaults={'email': email}
            )
            
            # Create teacher profile if it doesn't exist
            TeacherProfile.objects.get_or_create(
                teacher=teacher,
                defaults={
                    'bio': f'Experienced teacher {i}',
                    'gender': random.choice(['Male', 'Female', 'Rather not say']),
                    'phone_number': f'+1234567890{i}',
                    'date_of_birth': timezone.now().date() - timedelta(days=365*30)
                }
            )
            teachers.append(teacher)
            self.stdout.write(f'Created teacher {i}')

        # Create students
        students = []
        for i in range(20):
            username = f'student{i}'
            email = f'student{i}@example.com'
            
            # Create user if it doesn't exist
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'password': 'student123'
                }
            )
            if created:
                user.set_password('student123')
                user.save()
            
            # Add user to student group
            user.groups.add(student_group)
            
            # Create student if it doesn't exist
            student, created = Student.objects.get_or_create(
                user=user,
                defaults={'email': email}
            )
            
            # Create student profile if it doesn't exist
            StudentProfile.objects.get_or_create(
                student=student,
                defaults={
                    'bio': f'Student {i} profile',
                    'gender': random.choice(['Male', 'Female', 'Rather not say']),
                    'phone_number': f'+1234567890{i}',
                    'date_of_birth': timezone.now().date() - timedelta(days=365*18)
                }
            )
            students.append(student)
            self.stdout.write(f'Created student {i}')

        # Create courses
        courses = []
        subjects = ['Mathematics', 'Science', 'English', 'History', 'Computer Science']
        for i, subject in enumerate(subjects):
            course = Course.objects.create(
                course_id=f'C{i+1:03d}',
                course_name=f'{subject} 101',
                course_code=f'{subject[:3].upper()}{i+1:03d}',
                description=f'Introduction to {subject}',
                credits=3
            )
            courses.append(course)
            self.stdout.write(f'Created course {course.course_name}')

        # Create cohorts
        cohorts = []
        for i in range(3):
            cohort = Cohort.objects.create(
                cohort_id=f'CH{i+1:03d}',
                course=courses[i % len(courses)],
                name=f'Cohort {i+1}',
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timedelta(days=180)
            )
            cohorts.append(cohort)
            self.stdout.write(f'Created cohort {cohort.name}')

        # Create enrollments
        for student in students:
            # Get 2 random courses
            selected_courses = random.sample(courses, 2)
            for course in selected_courses:
                # Get a random cohort for this course
                course_cohorts = Cohort.objects.filter(course=course)
                if course_cohorts.exists():
                    cohort = random.choice(list(course_cohorts))
                    # Check if student is already enrolled in this cohort
                    if not Enrollment.objects.filter(student=student, cohort=cohort).exists():
                        Enrollment.objects.create(
                            student=student,
                            cohort=cohort,
                            status='active',
                            progress=0.0
                        )
                        self.stdout.write(f'Created enrollment for student {student.user.username} in cohort {cohort.name}')

        # Create units
        units = []
        unit_counter = 1  # Counter for unique unit codes
        for cohort in cohorts:
            for i in range(3):  # 3 units per cohort
                unit = Unit.objects.create(
                    unit_id=f'U{unit_counter:03d}',
                    cohort=cohort,
                    unit_name=f'Unit {i+1}',
                    unit_code=f'U{unit_counter:03d}',  # Use the counter for unique codes
                    description=f'Description for Unit {i+1}',
                    teacher=random.choice(teachers)
                )
                units.append(unit)
                unit_counter += 1  # Increment the counter
                self.stdout.write(f'Created unit {unit.unit_name} for cohort {cohort.name}')

        # Create lessons
        for unit in units:
            for i in range(4):  # 4 lessons per unit
                lesson = Lesson.objects.create(
                    unit=unit,
                    title=f'Lesson {i+1}',
                    description=f'Description for Lesson {i+1}',
                    class_type='PRERECORDED',
                    estimated_completion_time=60,
                    teacher=unit.teacher
                )
                self.stdout.write(f'Created lesson {lesson.title} for unit {unit.unit_name}')

                # Create topics for each lesson
                for j in range(3):  # 3 topics per lesson
                    topic = Topic.objects.create(
                        lesson=lesson,
                        title=f'Topic {j+1}',
                        content_type='TEXT',
                        content_text=f'Content for Topic {j+1}'
                    )
                    self.stdout.write(f'Created topic {topic.title} for lesson {lesson.title}')

                # Create one quiz per lesson (not per topic)
                quiz = Quiz.objects.create(
                    lesson=lesson,
                    name=f'Quiz for Lesson {lesson.title}',
                    desc=f'Test your knowledge of {lesson.title}',
                    number_of_questions=5,
                    time=300  # 5 minutes
                )
                self.stdout.write(f'Created quiz for lesson {lesson.title}')

                # Create questions for each quiz
                for k in range(5):  # 5 questions per quiz
                    question = Question.objects.create(
                        quiz=quiz,
                        question_content=f'Question {k+1} for {lesson.title}'
                    )
                    # Create answers for each question
                    for l in range(4):  # 4 answers per question
                        Answer.objects.create(
                            question=question,
                            content=f'Answer {l+1} for Question {k+1}',
                            correct=(l == 0)  # First answer is correct
                        )
                    self.stdout.write(f'Created question {k+1} for quiz {quiz.name}')

        # Create online classes
        for unit in units:
            for i in range(3):  # 3 online classes per unit
                OnlineClass.objects.create(
                    unit=unit,
                    title=f'Online Class {i+1}',
                    description=f'Description for Online Class {i+1}',
                    meeting_link=f'https://meet.google.com/abc-defg-hij',
                    meeting_platform='GOOGLE_MEET',
                    start_time=timezone.now() + timedelta(days=i),
                    duration=60  # 1 hour
                )
                self.stdout.write(f'Created online class for unit {unit.unit_name}')

        self.stdout.write(self.style.SUCCESS('Successfully populated dummy data'))
