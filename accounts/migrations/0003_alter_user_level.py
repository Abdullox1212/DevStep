# Generated by Django 5.1 on 2024-11-13 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_remove_user_league_user_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='level',
            field=models.IntegerField(default=1, max_length=100),
        ),
    ]
