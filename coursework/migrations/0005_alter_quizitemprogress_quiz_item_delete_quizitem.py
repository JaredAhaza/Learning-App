# Generated by Django 4.2.15 on 2024-09-02 22:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coursework', '0004_quiz_question_marks_of_user_answer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizitemprogress',
            name='quiz_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coursework.quiz'),
        ),
        migrations.DeleteModel(
            name='QuizItem',
        ),
    ]
