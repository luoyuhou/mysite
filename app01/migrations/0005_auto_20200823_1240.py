# Generated by Django 3.0.7 on 2020-08-23 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0004_auto_20200823_1235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sendmessage',
            name='from_user',
            field=models.IntegerField(default=0),
        ),
    ]
