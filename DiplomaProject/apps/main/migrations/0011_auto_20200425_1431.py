# Generated by Django 3.0.5 on 2020-04-25 11:31

from django.db import migrations, models
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_auto_20200425_1430'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testdictionary',
            name='file',
            field=models.FileField(default='some file', storage=main.models.OverwriteStorage(), upload_to=''),
        ),
        migrations.AlterField(
            model_name='testtext',
            name='file',
            field=models.FileField(default='some file', storage=main.models.OverwriteStorage(), upload_to=''),
        ),
        migrations.AlterField(
            model_name='traintext',
            name='file',
            field=models.FileField(default='some file', storage=main.models.OverwriteStorage(), upload_to=''),
        ),
    ]
