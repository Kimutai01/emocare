# Generated by Django 5.0.2 on 2024-02-29 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emotions', '0006_plans'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plans',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
