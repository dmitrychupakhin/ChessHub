# Generated by Django 5.0.2 on 2024-02-18 08:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0007_remove_chessgame_fen"),
    ]

    operations = [
        migrations.AddField(
            model_name="chessgame",
            name="black_rematch",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="chessgame",
            name="white_rematch",
            field=models.BooleanField(default=False),
        ),
    ]
