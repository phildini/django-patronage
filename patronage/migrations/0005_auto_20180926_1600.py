# Generated by Django 2.1 on 2018-09-26 16:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("patronage", "0004_tier_benefits")]

    operations = [
        migrations.RenameField(
            model_name="usertier", old_name="benefit", new_name="tier"
        )
    ]