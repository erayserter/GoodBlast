# Generated by Django 4.2.9 on 2024-02-04 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournament", "0002_remove_usertournamentgroup_entered_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="tournamentgroup",
            name="level_bucket",
            field=models.IntegerField(default=0),
        ),
    ]
