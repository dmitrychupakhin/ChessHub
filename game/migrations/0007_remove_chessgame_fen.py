# Generated by Django 5.0.2 on 2024-02-17 22:40

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0006_remove_chessgame_move_history_chessgame_pgn"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="chessgame",
            name="fen",
        ),
    ]
