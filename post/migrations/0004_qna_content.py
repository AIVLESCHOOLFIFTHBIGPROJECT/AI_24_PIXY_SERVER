# Generated by Django 5.0.6 on 2024-07-12 00:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("post", "0003_remove_answer_m_num_alter_qna_m_num"),
    ]

    operations = [
        migrations.AddField(
            model_name="qna",
            name="content",
            field=models.CharField(max_length=255, null=True),
        ),
    ]
