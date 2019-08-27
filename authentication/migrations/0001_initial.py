# Generated by Django 2.2.1 on 2019-08-26 07:31

from django.conf import settings
import django.contrib.postgres.fields.jsonb
import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import fernet_fields.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(
                    max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(
                    blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False,
                                                     help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True,
                                                max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True,
                                               max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False,
                                                 help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(
                    default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(
                    default=django.utils.timezone.now, verbose_name='date joined')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('username', models.CharField(blank=True,
                                              max_length=100, null=True, unique=True)),
                ('card_info', django.contrib.postgres.fields.jsonb.JSONField(
                    default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder, verbose_name='tokenized card details')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('role', models.CharField(choices=[('LA', 'LANDVILLE ADMIN'), ('CA', 'CLIENT ADMIN'), (
                    'BY', 'BUYER')], default='BY', max_length=2, verbose_name='user role')),
                ('is_verified', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
                                                  related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.',
                                                            related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BlackList',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('token', models.CharField(max_length=200, unique=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('approval_status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), (
                    'rejected', 'Rejected'), ('revoked', 'Revoked')], default='pending', max_length=10)),
                ('client_name', models.CharField(max_length=100, unique=True)),
                ('phone', models.CharField(max_length=17, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('address', django.contrib.postgres.fields.jsonb.JSONField(
                    encoder=django.core.serializers.json.DjangoJSONEncoder, verbose_name='physical address')),
                ('client_admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                                   related_name='employer', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ClientReview',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('review', models.TextField()),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                             related_name='reviewed_client', to='authentication.Client')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                               related_name='reviewer', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PasswordResetToken',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=400)),
                ('created', models.DateTimeField(auto_now=True)),
                ('is_valid', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('phone', models.CharField(max_length=17, null=True)),
                ('address', django.contrib.postgres.fields.jsonb.JSONField(
                    default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder, verbose_name='physical address')),
                ('user_level', models.CharField(choices=[('STARTER', 'STARTER'), ('BUYER', 'BUYER'), (
                    'INVESTOR', 'INVESTOR')], default='STARTER', max_length=20, verbose_name='user level')),
                ('image', models.URLField(blank=True, null=True)),
                ('security_question', models.CharField(choices=[('What is the name of your favorite childhood friend', 'What is the name of your favorite childhood friend'), (
                    'What was your childhood nickname', 'What was your childhood nickname'), ('In what city or town did your mother and father meet', 'In what city or town did your mother and father meet')], max_length=255, null=True)),
                ('security_answer', fernet_fields.fields.EncryptedTextField(null=True)),
                ('employer', models.CharField(blank=True, max_length=255, null=True)),
                ('designation', models.CharField(
                    blank=True, max_length=255, null=True)),
                ('next_of_kin', models.CharField(
                    blank=True, max_length=255, null=True)),
                ('next_of_kin_contact', models.CharField(
                    blank=True, max_length=17, null=True)),
                ('bio', models.TextField(blank=True, max_length=255)),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReplyReview',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('reply', models.TextField()),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                             related_name='replies', to='authentication.ClientReview')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                               related_name='reply', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
    ]
