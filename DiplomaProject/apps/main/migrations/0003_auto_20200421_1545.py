# Generated by Django 3.0.5 on 2020-04-21 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20200421_1538'),
    ]

    operations = [
        migrations.AddField(
            model_name='testtext',
            name='file',
            field=models.FileField(default='some file', upload_to=''),
        ),
        migrations.AddField(
            model_name='traintext',
            name='file',
            field=models.FileField(default='some file', upload_to=''),
        ),
    ]
