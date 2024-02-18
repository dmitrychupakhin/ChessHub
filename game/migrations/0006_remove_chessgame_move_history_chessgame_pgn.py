# Generated by Django 5.0.2 on 2024-02-17 22:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0005_chessgame_move_history"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="chessgame",
            name="move_history",
        ),
        migrations.AddField(
            model_name="chessgame",
            name="pgn",
            field=models.TextField(default=""),
        ),
    ]