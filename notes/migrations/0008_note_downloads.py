# Generated by Django 5.1.2 on 2024-10-28 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0007_feedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='downloads',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
