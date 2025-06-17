# coursework/models.py
from django.db import models
from accounts.models import StudentProfile, Student
from tinymce.models import HTMLField
from django.utils import timezone

class Course(models.Model):
    course_id = models.CharField(max_length=10, primary_key=True)
    course_name = models.CharField(max_length=255)
    course_code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True, max_length=500)
    instructions = models.TextField(blank=True, null=True, max_length=500)
    credits = models.PositiveIntegerField()  # or use hours = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.course_name} ({self.course_code})"

class Cohort(models.Model):
    cohort_id = models.CharField(max_length=10, primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='cohorts')
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.course.course_code})"

    def students(self):
        """Return all students enrolled in this cohort."""
        return [enrollment.student for enrollment in self.enrollment_set.select_related('student')]

class Enrollment(models.Model):
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE)
    cohort = models.ForeignKey('Cohort', on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped')
    ], default='active')
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # e.g., 75.00 for 75%

    class Meta:
        unique_together = ('student', 'cohort')

    def __str__(self):
        return f"{self.student} - {self.cohort} ({self.status})"

class EnrollmentRequest(models.Model):
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE)
    cohort = models.ForeignKey('Cohort', on_delete=models.CASCADE)
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')
    notes = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey('accounts.Teacher', on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'cohort')

    def __str__(self):
        return f"{self.student} - {self.cohort} ({self.status})"

class TimeSlot(models.Model):
    """Represents a time slot in the timetable."""
    DAYS_OF_WEEK = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
    ]
    
    TIME_SLOTS = [
        ('07:00', '07:00 AM'),
        ('08:00', '08:00 AM'),
        ('09:00', '09:00 AM'),
        ('10:00', '10:00 AM'),
        ('11:00', '11:00 AM'),
        ('12:00', '12:00 PM'),
        ('13:00', '01:00 PM'),
        ('14:00', '02:00 PM'),
        ('15:00', '03:00 PM'),
        ('16:00', '04:00 PM'),
        ('17:00', '05:00 PM'),
        ('18:00', '06:00 PM'),
    ]

    day = models.CharField(max_length=3, choices=DAYS_OF_WEEK)
    start_time = models.CharField(max_length=5, choices=TIME_SLOTS)
    end_time = models.CharField(max_length=5, choices=TIME_SLOTS, blank=True, null=True)
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE, related_name='time_slots')
    teacher = models.ForeignKey('accounts.Teacher', on_delete=models.CASCADE, related_name='time_slots')
    is_booked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('day', 'start_time', 'teacher')
        ordering = ['day', 'start_time']

    def __str__(self):
        if self.end_time:
            return f"{self.get_day_display()} {self.get_start_time_display()} - {self.get_end_time_display()} - {self.lesson.title}"
        return f"{self.get_day_display()} {self.get_start_time_display()} - {self.lesson.title}"

    def save(self, *args, **kwargs):
        """Override save to automatically calculate end_time based on lesson duration."""
        if not self.end_time and self.lesson and self.lesson.estimated_completion_time:
            # Calculate end time based on lesson duration
            start_hour, start_minute = map(int, self.start_time.split(':'))
            duration_minutes = self.lesson.estimated_completion_time
            
            # Calculate end time
            total_minutes = start_hour * 60 + start_minute + duration_minutes
            end_hour = total_minutes // 60
            end_minute = total_minutes % 60
            
            # Format end time
            self.end_time = f"{end_hour:02d}:{end_minute:02d}"
        
        super().save(*args, **kwargs)

    @classmethod
    def get_all_time_slots(cls):
        """Returns all possible time slots for the week."""
        all_slots = []
        for day, _ in cls.DAYS_OF_WEEK:
            for time, _ in cls.TIME_SLOTS:
                all_slots.append((day, time))
        return all_slots

    @classmethod
    def get_booked_slots(cls, teacher=None):
        """Returns all booked time slots, optionally filtered by teacher."""
        query = cls.objects.filter(is_booked=True)
        if teacher:
            query = query.filter(teacher=teacher)
        return query

    @classmethod
    def get_free_slots(cls, teacher=None):
        """Returns all free time slots, optionally filtered by teacher."""
        all_slots = set(cls.get_all_time_slots())
        booked_slots = set(cls.get_booked_slots(teacher).values_list('day', 'start_time'))
        return all_slots - booked_slots

class Lesson(models.Model):
    """Represents a lesson within a unit."""
    CLASS_TYPES = [
        ('ONLINE', 'Online Class'),
        ('PRERECORDED', 'Pre-recorded Video'),
    ]
    
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    description = models.TextField()
    class_type = models.CharField(max_length=20, choices=CLASS_TYPES, default='PRERECORDED')
    content = HTMLField(blank=True, null=True)  # For rich text content
    
    # Online class specific fields
    meeting_link = models.URLField(blank=True, null=True, help_text="Zoom or Google Meet link for online classes")
    meeting_platform = models.CharField(max_length=20, choices=[
        ('ZOOM', 'Zoom'),
        ('GOOGLE_MEET', 'Google Meet'),
        ('OTHER', 'Other')
    ], blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    duration = models.PositiveIntegerField(help_text="Duration in minutes", blank=True, null=True)
    
    # Pre-recorded video specific fields
    video_url = models.URLField(blank=True, null=True, help_text="URL to pre-recorded video content")
    
    # Common fields
    reading_materials = models.FileField(upload_to='lessons/materials/', blank=True, null=True, help_text="PDF or other reading materials")
    estimated_completion_time = models.PositiveIntegerField(help_text="Estimated time to complete this lesson in minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    teacher = models.ForeignKey('accounts.Teacher', on_delete=models.SET_NULL, null=True, related_name='lessons')

    class Meta:
        ordering = ['created_at']

    def get_timetable_slots(self):
        """Returns all time slots for this lesson."""
        return self.time_slots.all()

    def get_status_display(self):
        """Get the display status of the lesson."""
        if self.class_type == 'PRERECORDED':
            return 'Video Lesson'
        elif self.is_upcoming():
            return 'Upcoming Live Lesson'
        elif self.is_ongoing():
            return 'Live Lesson'
        else:
            return 'Ended'

    def get_completion_percentage(self, student):
        """Returns the completion percentage of the lesson for the given student."""
        lesson_progress = LessonProgress.objects.get(student=student, lesson=self)
        if not lesson_progress.opened:
            return 0  # Lesson not opened, 0% completion

        topics = self.topic_set.all()
        completed_topics = TopicProgress.objects.filter(student=student, topic__in=topics, completed=True)
        total_topics = topics.count()
        if total_topics == 0:
            return 100  # No topics, 100% completion

        completion_percentage = (completed_topics.count() / total_topics) * 100
        return completion_percentage

    def get_formatted_duration(self):
        """Returns the estimated completion time in a human-readable format."""
        try:
            # Handle integer value (minutes)
            total_minutes = int(self.estimated_completion_time)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            
            if hours > 0:
                return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        except (ValueError, TypeError):
            # If the value is not an integer, return a default message
            return "Time not specified"

    def is_upcoming(self):
        """Check if the online class is upcoming."""
        if self.class_type != 'ONLINE' or not self.start_time:
            return False
        return self.start_time > timezone.now()

    def is_ongoing(self):
        """Check if the online class is currently ongoing."""
        if self.class_type != 'ONLINE' or not self.start_time or not self.duration:
            return False
        now = timezone.now()
        end_time = self.start_time + timezone.timedelta(minutes=self.duration)
        return self.start_time <= now <= end_time

    def has_ended(self):
        """Check if the online class has ended."""
        if self.class_type != 'ONLINE' or not self.start_time or not self.duration:
            return False
        end_time = self.start_time + timezone.timedelta(minutes=self.duration)
        return end_time < timezone.now()

    def get_status(self):
        """Get the current status of the lesson."""
        if self.class_type == 'PRERECORDED':
            return 'prerecorded'
        elif self.is_upcoming():
            return 'upcoming'
        elif self.is_ongoing():
            return 'ongoing'
        else:
            return 'ended'

    def __str__(self):
        return f"{self.title} - {self.unit.unit_name}"

class LessonProgress(models.Model):
    """Represents a student's progress on a lesson."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    opened = models.BooleanField(default=False)  # Has the student opened the lesson?
    completed = models.BooleanField(default=False)  # Has the student completed the lesson?
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.lesson.title}"

class Topic(models.Model):
    """Represents a short topic within a lesson."""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=10, choices=[
        ('TEXT', 'Text'),
        ('PDF', 'PDF'),
        ('VIDEO', 'Video')
    ])
    content_text = models.TextField(blank=True, null=True)
    content_pdf = models.FileField(upload_to='topics/pdfs/', blank=True, null=True)
    content_video = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Quiz(models.Model):
    """Represents a quiz item (question and answers) associated with a topic."""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    desc = models.CharField(max_length=500)    
    number_of_questions = models.IntegerField(default=1)
    time = models.IntegerField(help_text="Duration of the quiz in seconds", default="1")
    
    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'
        
    def __str__(self):
        return self.name

    def __str__(self):
        return f"{self.topic.title} - {self.question}"
    
    def get_questions(self):
        return self.question_set.all()
    
class Question(models.Model):
    question_content = models.CharField(max_length=200)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.content
    
    def get_answers(self):
        return self.answer_set.all()
    
    
class Answer(models.Model):
    content = models.CharField(max_length=200)
    correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"question: {self.question.content}, answer: {self.content}, correct: {self.correct}"
    
class Marks_Of_User(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.StudentProfile', on_delete=models.CASCADE)
    score = models.FloatField()
    
    def __str__(self):
        return f"{self.student.name} - {str(self.quiz)}"

class TopicProgress(models.Model):
    """Represents a student's progress on a topic."""
    student = models.ForeignKey('accounts.StudentProfile', on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    opened = models.BooleanField(default=False)  # Has the student opened the topic?
    completed = models.BooleanField(default=False)  # Has the student completed the topic?
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.topic.title}"

class QuizItemProgress(models.Model):
    """Represents a student's progress on a quiz item."""
    student = models.ForeignKey('accounts.StudentProfile', on_delete=models.CASCADE)
    quiz_item = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    answered = models.BooleanField(default=False)  # Has the student answered the quiz item?
    correct = models.BooleanField(default=False)  # Is the student's answer correct?
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.quiz_item.topic.title} - {self.quiz_item.question}"

class Unit(models.Model):
    unit_id = models.CharField(max_length=10, primary_key=True)
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name='units')
    unit_name = models.CharField(max_length=255)
    unit_code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    learning_outcomes = models.TextField(blank=True, null=True)
    teacher = models.ForeignKey('accounts.Teacher', on_delete=models.SET_NULL, null=True, related_name='units')

    def __str__(self):
        return f"{self.unit_name} ({self.unit_code})"

class OnlineClass(models.Model):
    """Represents an online class session."""
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='online_classes')
    title = models.CharField(max_length=255)
    description = models.TextField()
    meeting_link = models.URLField(help_text="Zoom or Google Meet link")
    meeting_platform = models.CharField(max_length=20, choices=[
        ('ZOOM', 'Zoom'),
        ('GOOGLE_MEET', 'Google Meet'),
        ('OTHER', 'Other')
    ])
    start_time = models.DateTimeField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.title} - {self.unit.unit_name}"

    def is_upcoming(self):
        """Check if the class is upcoming."""
        return self.start_time > timezone.now()

    def is_ongoing(self):
        """Check if the class is currently ongoing."""
        now = timezone.now()
        end_time = self.start_time + timezone.timedelta(minutes=self.duration)
        return self.start_time <= now <= end_time

    def has_ended(self):
        """Check if the class has ended."""
        end_time = self.start_time + timezone.timedelta(minutes=self.duration)
        return end_time < timezone.now()

    def get_status(self):
        """Get the current status of the class."""
        if self.is_upcoming():
            return 'upcoming'
        elif self.is_ongoing():
            return 'ongoing'
        else:
            return 'ended'

    def get_end_time(self):
        """Get the end time of the class."""
        return self.start_time + timezone.timedelta(minutes=self.duration)

    def to_timetable_slot(self):
        """Convert online class to timetable slot format."""
        if not self.start_time:
            return None
            
        class_day = self.start_time.strftime('%a').upper()[:3]
        class_time = self.start_time.strftime('%H:%M')
        
        # Find the closest time slot
        closest_time = None
        for time_code, time_display in TimeSlot.TIME_SLOTS:
            if time_code == class_time:
                closest_time = time_code
                break
        
        # If no exact match, find the closest time slot
        if not closest_time:
            class_hour = int(class_time.split(':')[0])
            class_minute = int(class_time.split(':')[1])
            
            # Find the closest predefined time slot
            min_diff = float('inf')
            for time_code, time_display in TimeSlot.TIME_SLOTS:
                slot_hour = int(time_code.split(':')[0])
                slot_minute = int(time_code.split(':')[1])
                
                diff = abs((class_hour * 60 + class_minute) - (slot_hour * 60 + slot_minute))
                if diff < min_diff:
                    min_diff = diff
                    closest_time = time_code
        
        # Create a mock TimeSlot object
        class_slot = type('MockTimeSlot', (), {
            'day': class_day,
            'start_time': closest_time,
            'lesson': type('MockLesson', (), {
                'title': self.title,
                'class_type': 'ONLINE',
                'meeting_link': self.meeting_link,
                'unit': self.unit,
                'get_status_display': lambda: 'Online Class',
                'get_class_type_display': lambda: 'Online Class'
            })(),
            'is_booked': True
        })()
        
        return class_slot
