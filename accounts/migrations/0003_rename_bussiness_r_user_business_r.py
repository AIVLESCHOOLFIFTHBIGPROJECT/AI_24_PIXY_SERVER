from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_user_is_agreement1_user_is_agreement2_and_more"),
    ]

    operations = [
        migrations.RunPython(lambda apps, schema_editor: None, lambda apps, schema_editor: None)
    ]