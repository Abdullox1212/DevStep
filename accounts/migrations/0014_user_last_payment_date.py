# Generated by Django 5.1 on 2024-12-22 05:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_user_payment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_payment_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
