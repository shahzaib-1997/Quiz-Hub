# Generated by Django 4.2.3 on 2023-07-15 11:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("quiz_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="QuizQuestions",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("question_with_choices", models.TextField()),
                ("correct_option", models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name="Topic",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("topic", models.CharField(max_length=255)),
            ],
        ),
        migrations.DeleteModel(
            name="Quiz",
        ),
        migrations.AddField(
            model_name="quizquestions",
            name="topic",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="quiz_app.topic"
            ),
        ),
    ]