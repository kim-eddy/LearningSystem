# Generated migration for adding language preferences

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MyProject', '0007_remove_badges_student'),  # Adjust to your latest migration
    ]

    operations = [
        migrations.AddField(
            model_name='student_profile',
            name='preferred_language',
            field=models.CharField(
                choices=[
                    ('en', 'English'),
                    ('sw', 'Kiswahili'),
                    ('sheng', "Sheng'"),
                    ('ki', 'Kikuyu'),
                    ('so', 'Kisomali'),
                ],
                default='en',
                help_text='Select your preferred language for the platform',
                max_length=10,
            ),
        ),
    ]
