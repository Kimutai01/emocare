# Generated by Django 5.0.2 on 2024-02-25 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emotions', '0002_emotion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emotion',
            name='emotions',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
