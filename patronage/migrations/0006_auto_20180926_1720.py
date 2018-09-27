# Generated by Django 2.1.1 on 2018-09-26 17:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('patronage', '0005_auto_20180926_1600'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tier',
            name='remote_benefit_id',
        ),
        migrations.RemoveField(
            model_name='tier',
            name='remote_benefit_title',
        ),
        migrations.AddField(
            model_name='tier',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]