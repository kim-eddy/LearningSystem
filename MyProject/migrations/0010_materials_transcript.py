from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("MyProject", "0009_resources"),
    ]

    operations = [
        migrations.AddField(
            model_name="materials",
            name="transcript",
            field=models.TextField(
                blank=True,
                null=True,
                help_text="Optional transcript text for audio/video materials",
            ),
        ),
    ]
