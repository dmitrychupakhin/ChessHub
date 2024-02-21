# Generated by Django 5.0.2 on 2024-02-21 15:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "game",
            "0014_rename_black_user_end_time_chessgame_black_user_total_time_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="chessgame",
            name="black_user_total_time",
        ),
        migrations.RemoveField(
            model_name="chessgame",
            name="white_user_total_time",
        ),
        migrations.AddField(
            model_name="chessgame",
            name="black_user_end_time",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="chessgame",
            name="white_user_end_time",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
