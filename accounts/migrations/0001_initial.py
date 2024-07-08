# Generated by Django 5.0.6 on 2024-07-08 03:44

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=100, unique=True, verbose_name="email"
                    ),
                ),
                ("name", models.CharField(max_length=30)),
                ("p_num", models.CharField(max_length=30)),
                ("r_num", models.CharField(max_length=30)),
                (
                    "business_r",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to=accounts.models.User.date_upload_to,
                        verbose_name="사업자등록증",
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("is_admin", models.BooleanField(default=False)),
                ("is_agreement1", models.BooleanField(default=False)),
                ("is_agreement2", models.BooleanField(default=False)),
                ("is_agreement3", models.BooleanField(default=False, null=True)),
            ],
            options={
                "db_table": "user",
            },
        ),
    ]
