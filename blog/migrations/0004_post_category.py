# Generated by Django 3.2 on 2022-11-20 08:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20221120_1213'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='category',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.PROTECT, related_name='posts', to='blog.category'),
            preserve_default=False,
        ),
    ]
