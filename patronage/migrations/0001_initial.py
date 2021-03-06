# Generated by Django 2.0.8 on 2018-08-20 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Benefit",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("campaign_id", models.CharField(max_length=100, null=True)),
                ("tier_id", models.CharField(max_length=100, null=True)),
                ("remote_benefit_id", models.CharField(max_length=100, null=True)),
                ("remote_benefit_title", models.CharField(max_length=100, null=True)),
                ("tier_title", models.CharField(max_length=100, null=True)),
                ("campaign_title", models.CharField(max_length=255, null=True)),
                ("tier_amount_cents", models.IntegerField(null=True)),
            ],
        )
    ]
