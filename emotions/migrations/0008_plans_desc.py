# Generated by Django 5.0.2 on 2024-02-29 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emotions', '0007_alter_plans_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='plans',
            name='desc',
            field=models.TextField(null=True),
        ),
    ]
