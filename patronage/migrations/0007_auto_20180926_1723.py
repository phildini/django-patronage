# Generated by Django 2.1.1 on 2018-09-26 17:23

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('patronage', '0006_auto_20180926_1720'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tier',
            name='creator',
        ),
        migrations.AddField(
            model_name='tier',
            name='creators',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
