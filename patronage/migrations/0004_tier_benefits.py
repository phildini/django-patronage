# Generated by Django 2.1 on 2018-09-04 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("patronage", "0003_auto_20180904_1127")]

    operations = [
        migrations.AddField(
            model_name="tier",
            name="benefits",
            field=models.ManyToManyField(to="patronage.RemoteBenefit"),
        )
    ]
