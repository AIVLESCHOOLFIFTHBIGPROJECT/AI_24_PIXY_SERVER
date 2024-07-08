# Generated by Django 5.0.6 on 2024-07-08 15:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Qna",
            fields=[
                ("b_num", models.BigAutoField(primary_key=True, serialize=False)),
                ("m_num", models.BigIntegerField()),
                ("title", models.CharField(max_length=255)),
                ("c_date", models.DateTimeField(auto_now_add=True)),
                ("m_date", models.DateTimeField(auto_now=True)),
                ("viewcnt", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Answer",
            fields=[
                ("a_num", models.BigAutoField(primary_key=True, serialize=False)),
                ("m_num", models.BigIntegerField()),
                ("content", models.CharField(max_length=255)),
                ("c_date", models.DateTimeField(auto_now_add=True)),
                ("m_date", models.DateTimeField(auto_now=True)),
                (
                    "b_num",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="post.qna"
                    ),
                ),
            ],
        ),
    ]