# Generated by Django 5.0.2 on 2024-03-01 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emotions', '0012_alter_emotion_probability'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=100, null=True, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
