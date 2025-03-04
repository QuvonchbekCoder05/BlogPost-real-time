# Generated by Django 5.1.6 on 2025-03-03 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('content', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='posts/images/')),
                ('background_image', models.ImageField(blank=True, null=True, upload_to='posts/backgrounds/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
