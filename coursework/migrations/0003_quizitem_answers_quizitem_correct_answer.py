# Generated by Django 4.2.15 on 2024-09-02 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coursework', '0002_course_description_course_duration_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizitem',
            name='answers',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='quizitem',
            name='correct_answer',
            field=models.TextField(blank=True, null=True),
        ),
    ]
