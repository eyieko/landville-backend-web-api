# Generated by Django 2.2.1 on 2019-08-08 13:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0004_term_last_updated'),
    ]

    operations = [
        migrations.RenameField(
            model_name='term',
            old_name='last_updated',
            new_name='last_updated_at',
        ),
    ]
