# coursework/models.py
from django.db import models
from accounts.models import StudentProfile, Student

class Course(models.Model):
    """Represents a course offered by the college."""
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructions = models.TextField()
    duration = models.CharField(max_length=50)  # e.g., "8 weeks"
    created_at = models.DateTimeField(auto_now_add=True)
    student = models.ManyToManyField('accounts.Student')


    def __str__(self):
        return self.title

    def get_lessons(self):
        """Returns a list of lessons associated with the course."""
        student_id = self.student_id
        return Lesson.objects.filter(course=self)
    
    def get_completion_percentage(self, student):
        """Returns the completion percentage of the course for the given student."""
        lessons = self.lesson_set.all()
        total_lessons = lessons.count()
        completed_lessons = 0

        for lesson in lessons:
            lesson_progress = LessonProgress.objects.get(student=student, lesson=lesson)
            if lesson_progress.completed:
                completed_lessons += 1

        completion_percentage = (completed_lessons / total_lessons) * 100
        return completion_percentage  

class Enrollment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.course.title}"

class Lesson(models.Model):
    """Represents a lesson within a course."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

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

    def __str__(self):
        return self.title
    
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
