# Generated by Django 5.0 on 2024-02-02 04:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_payments", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="userpayments",
            name="stripe_customer_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
