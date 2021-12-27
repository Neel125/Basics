# Generated by Django 2.2.22 on 2021-05-17 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Sentiment', '0002_document_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_superuser',
            field=models.BooleanField(default=False),
        ),
    ]
