# Generated by Django 3.0.4 on 2020-03-31 22:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifier', '0004_auto_20200331_1348'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pastshift',
            options={},
        ),
        migrations.AlterModelOptions(
            name='shift',
            options={},
        ),
        migrations.RemoveField(
            model_name='pastshift',
            name='date',
        ),
        migrations.RemoveField(
            model_name='pastshift',
            name='end',
        ),
        migrations.RemoveField(
            model_name='pastshift',
            name='start',
        ),
        migrations.RemoveField(
            model_name='shift',
            name='date',
        ),
        migrations.RemoveField(
            model_name='shift',
            name='end',
        ),
        migrations.RemoveField(
            model_name='shift',
            name='start',
        ),
        migrations.AddField(
            model_name='pastshift',
            name='day',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pastshift',
            name='end_hour',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pastshift',
            name='end_min',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pastshift',
            name='month',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pastshift',
            name='start_hour',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pastshift',
            name='start_min',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pastshift',
            name='year',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shift',
            name='day',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shift',
            name='end_hour',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shift',
            name='end_min',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shift',
            name='month',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shift',
            name='start_hour',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shift',
            name='start_min',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shift',
            name='year',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
