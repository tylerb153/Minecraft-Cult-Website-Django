# Generated by Django 5.2 on 2025-05-24 07:26

import django.db.models.deletion
import showcase.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('showcase', '0004_alter_image_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='build',
            name='thumbnail',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Thumbnail', to='showcase.image'),
        ),
        migrations.AlterField(
            model_name='image',
            name='build',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='images', to='showcase.build'),
        ),
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(upload_to=showcase.models.build_image_upload_path),
        ),
    ]
