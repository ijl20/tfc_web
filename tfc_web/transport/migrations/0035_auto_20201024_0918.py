# Generated by Django 2.2.10 on 2020-10-24 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0034_auto_20201022_1418'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehiclejourney',
            name='journey_pattern',
        ),
        migrations.AddField(
            model_name='vehiclejourney',
            name='journey_pattern_ref',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
