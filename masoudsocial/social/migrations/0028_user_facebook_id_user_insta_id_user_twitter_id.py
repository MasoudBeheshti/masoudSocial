# Generated by Django 5.0.4 on 2024-05-23 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0027_rename_total_saved_post_total_saves'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='facebook_id',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='insta_id',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='twitter_id',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
