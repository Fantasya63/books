# Generated by Django 5.0.5 on 2024-05-23 03:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0017_rename_product_order_items'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='date',
            new_name='datetime',
        ),
    ]
