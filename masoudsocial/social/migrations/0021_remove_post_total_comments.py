# Generated by Django 5.0.4 on 2024-05-20 18:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0020_post_total_comments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='total_comments',
        ),
    ]
