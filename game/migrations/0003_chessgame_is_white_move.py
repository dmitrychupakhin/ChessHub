# Generated by Django 5.0.2 on 2024-02-17 08:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0002_chessgame_is_public"),
    ]

    operations = [
        migrations.AddField(
            model_name="chessgame",
            name="is_white_move",
            field=models.BooleanField(default=True),
        ),
    ]
