# Generated by Django 5.0 on 2024-03-11 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_payments', '0006_userpayments_subscription_number'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userpayments',
            old_name='stripe_customer',
            new_name='customer_id',
        ),
        migrations.RenameField(
            model_name='userpayments',
            old_name='stripe_subscription_id',
            new_name='subscription_id',
        ),
        migrations.RenameField(
            model_name='userpayments',
            old_name='subscription_type',
            new_name='subscription_name',
        ),
        migrations.RemoveField(
            model_name='userpayments',
            name='subscription_number',
        ),
        migrations.AddField(
            model_name='userpayments',
            name='checkout_id',
            field=models.CharField(default='', max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userpayments',
            name='last_payment_subscription_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='userpayments',
            name='price_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='userpayments',
            name='upgrade',
            field=models.BooleanField(default=False),
        ),
    ]
