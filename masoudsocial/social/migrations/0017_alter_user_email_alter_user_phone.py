# Generated by Django 5.0.4 on 2024-05-16 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0016_alter_ticket_subject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.CharField(default='', max_length=50, verbose_name='ایمیل'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(default='', max_length=11, verbose_name='شماره تلفن'),
        ),
    ]
