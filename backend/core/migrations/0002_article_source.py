# Generated by Django 5.2.4 on 2025-07-26 01:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='source',
            field=models.CharField(default='CNN', max_length=50),
        ),
    ]
