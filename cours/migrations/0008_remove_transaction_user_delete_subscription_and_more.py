# Generated by Django 4.2.6 on 2024-07-15 19:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cours', '0007_alter_transaction_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='user',
        ),
        migrations.DeleteModel(
            name='Subscription',
        ),
        migrations.DeleteModel(
            name='Transaction',
        ),
    ]
