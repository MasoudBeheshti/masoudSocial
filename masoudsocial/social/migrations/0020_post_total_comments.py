# Generated by Django 5.0.4 on 2024-05-20 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0019_ticket_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='total_comments',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
