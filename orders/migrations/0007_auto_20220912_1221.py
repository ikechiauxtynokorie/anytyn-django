# Generated by Django 3.1 on 2022-09-12 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_auto_20220612_1804'),
        ('orders', '0006_auto_20220912_1206'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderproduct',
            name='variation',
        ),
        migrations.AddField(
            model_name='orderproduct',
            name='variation',
            field=models.ManyToManyField(blank=True, to='store.Variation'),
        ),
    ]
