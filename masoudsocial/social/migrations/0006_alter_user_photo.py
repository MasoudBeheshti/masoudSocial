# Generated by Django 5.0.4 on 2024-04-29 08:29

import django_resized.forms
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0005_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=django_resized.forms.ResizedImageField(blank=True, crop=['middle', 'center'], force_format=None, keep_meta=True, null=True, quality=60, scale=None, size=[500, 500], upload_to='account_images/', verbose_name='تصویر'),
        ),
    ]
