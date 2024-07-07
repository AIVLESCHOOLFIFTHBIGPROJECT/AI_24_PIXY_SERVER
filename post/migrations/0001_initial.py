# Generated by Django 4.2 on 2024-07-05 02:24

from django.db import migrations, models
import django.db.models.deletion


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
                ("c_date", models.CharField(max_length=255)),
                ("m_date", models.CharField(max_length=255)),
                ("viewcnt", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Answer",
            fields=[
                ("a_num", models.BigAutoField(primary_key=True, serialize=False)),
                ("m_num", models.BigIntegerField()),
                ("content", models.CharField(max_length=255)),
                ("c_date", models.CharField(max_length=255)),
                ("m_date", models.CharField(max_length=255)),
                (
                    "b_num",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="post.qna"
                    ),
                ),
            ],
        ),
    ]
