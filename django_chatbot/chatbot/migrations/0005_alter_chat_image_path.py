# Generated by Django 5.0 on 2024-01-07 21:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chatbot", "0004_alter_chat_image_path"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chat",
            name="image_path",
            field=models.ImageField(blank=True, null=True, upload_to=""),
        ),
    ]
