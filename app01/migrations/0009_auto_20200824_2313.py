# Generated by Django 3.0.7 on 2020-08-24 23:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0008_auto_20200824_2222'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notice',
            name='update_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]