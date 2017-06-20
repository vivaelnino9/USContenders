# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-06-20 20:38
from __future__ import unicode_literals

import datetime
from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0007_alter_validators_add_error_messages'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=30, unique=True, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.')], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('team', models.CharField(blank=True, default='', max_length=50, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('played', models.BooleanField(default=False, verbose_name='Played?')),
                ('map', models.CharField(max_length=50, verbose_name='Map')),
                ('challenge_date', models.DateField(default=datetime.date.today, verbose_name='Challenge Date')),
                ('forfeit_date', models.DateField(default=datetime.date(2017, 6, 25), verbose_name='Forfeit Date')),
                ('void_date', models.DateField(default=datetime.date(2017, 7, 4), verbose_name='Void Date')),
                ('play_date', models.DateField(blank=True, null=True, verbose_name='Date Played')),
                ('approved', models.BooleanField(default=False, verbose_name='Approved?')),
            ],
            options={
                'db_table': 'challenges',
            },
        ),
        migrations.CreateModel(
            name='FreeAgent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('eligible', models.BooleanField(default=True, verbose_name='Eligible?')),
                ('server', models.IntegerField(choices=[(1, 'Radius'), (2, 'Pi'), (3, 'Origin'), (4, 'Sphere'), (5, 'Centra'), (6, 'Orbit'), (7, 'Chord'), (8, 'Diameter'), (9, 'Any')], verbose_name='Server')),
                ('position', models.IntegerField(choices=[(1, 'O'), (2, 'D'), (3, 'O/D'), (4, 'D/O'), (5, 'Any')], verbose_name='Position')),
                ('mic', models.BooleanField(default=True, verbose_name='Mic?')),
                ('tagpro_profile', models.URLField(blank=True, null=True, verbose_name='TagPro Profile')),
                ('reddit_info', models.URLField(blank=True, null=True, verbose_name='Reddit Info')),
                ('tagpro_stats', models.URLField(blank=True, null=True, verbose_name='TagPro Stats')),
                ('additional_notes', models.TextField(blank=True, max_length=500, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'db_table': 'free_agents',
            },
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('minutes', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('tags', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('captures', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('hold', models.CharField(blank=True, default=0, max_length=10, null=True)),
                ('returns', models.PositiveIntegerField(blank=True, default=0, null=True)),
            ],
            options={
                'db_table': 'players',
            },
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_id', models.PositiveIntegerField(blank=True, null=True, verbose_name='Match ID')),
                ('team1', models.CharField(blank=True, max_length=50, null=True, verbose_name='Team 1')),
                ('team2', models.CharField(blank=True, max_length=50, null=True, verbose_name='Team 2')),
                ('team1_score', models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Score 1')),
                ('team2_score', models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Score 2')),
            ],
            options={
                'db_table': 'results',
            },
        ),
        migrations.CreateModel(
            name='Roster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_name', models.CharField(max_length=50)),
                ('abv', models.CharField(max_length=4)),
                ('rank', models.PositiveIntegerField()),
                ('firstActive', models.DateField(blank=True, null=True)),
                ('daysActive', models.PositiveIntegerField()),
                ('server', models.IntegerField(choices=[(1, 'Radius'), (2, 'Pi'), (3, 'Origin'), (4, 'Sphere'), (5, 'Centra'), (6, 'Orbit'), (7, 'Chord'), (8, 'Diameter'), (9, 'Any')], verbose_name='Server')),
                ('logo', models.ImageField(blank=True, upload_to='photos', verbose_name='logo')),
            ],
            options={
                'db_table': 'rosters',
            },
        ),
        migrations.CreateModel(
            name='Stats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('change', models.IntegerField(blank=True, default=0, null=True)),
                ('team', models.CharField(max_length=50)),
                ('abv', models.CharField(max_length=4)),
                ('streak', models.IntegerField(blank=True, default=0, null=True)),
                ('highestRank', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('uscmRank', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('lastActive', models.DateField(blank=True, null=True)),
                ('GP', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('W', models.IntegerField(blank=True, default=0, null=True)),
                ('L', models.IntegerField(blank=True, default=0, null=True)),
                ('D', models.IntegerField(blank=True, default=0, null=True)),
                ('F', models.IntegerField(blank=True, default=0, null=True)),
                ('CF', models.IntegerField(blank=True, default=0, null=True)),
                ('CA', models.IntegerField(blank=True, default=0, null=True)),
                ('CD', models.IntegerField(blank=True, default=0, null=True)),
                ('CDperG', models.FloatField(blank=True, default=0, null=True, verbose_name='CD/G')),
                ('rank_points', models.PositiveIntegerField(blank=True, default=0, null=True)),
            ],
            options={
                'db_table': 'stats',
            },
        ),
        migrations.CreateModel(
            name='Captain',
            fields=[
                ('player_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='usc_app.Player')),
            ],
            options={
                'db_table': 'captains',
            },
            bases=('usc_app.player',),
        ),
        migrations.AddField(
            model_name='roster',
            name='co_captain',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='co_captain', to='usc_app.Player', verbose_name='Co-Captain'),
        ),
        migrations.AddField(
            model_name='roster',
            name='member1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='member1', to='usc_app.Player', verbose_name='Member1'),
        ),
        migrations.AddField(
            model_name='roster',
            name='member2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='member2', to='usc_app.Player', verbose_name='Member2'),
        ),
        migrations.AddField(
            model_name='roster',
            name='member3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='member3', to='usc_app.Player', verbose_name='Member3'),
        ),
        migrations.AddField(
            model_name='roster',
            name='member4',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='member4', to='usc_app.Player', verbose_name='Member4'),
        ),
        migrations.AddField(
            model_name='roster',
            name='member5',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='member5', to='usc_app.Player', verbose_name='Member5'),
        ),
        migrations.AddField(
            model_name='roster',
            name='member6',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='member6', to='usc_app.Player', verbose_name='Member6'),
        ),
        migrations.AddField(
            model_name='player',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='challenge',
            name='challenged',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='challenged', to='usc_app.Roster', verbose_name='Challenged'),
        ),
        migrations.AddField(
            model_name='challenge',
            name='challenger',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='challenger', to='usc_app.Roster', verbose_name='Challenger'),
        ),
        migrations.AddField(
            model_name='challenge',
            name='g1_results',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='g1_results', to='usc_app.Result', verbose_name='Game 1 Results'),
        ),
        migrations.AddField(
            model_name='challenge',
            name='g1_submitted',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='g1_submitted', to='usc_app.Result', verbose_name='Game 1 Submitted'),
        ),
        migrations.AddField(
            model_name='challenge',
            name='g2_results',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='g2_results', to='usc_app.Result', verbose_name='Game 2 Results'),
        ),
        migrations.AddField(
            model_name='challenge',
            name='g2_submitted',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='g2_submitted', to='usc_app.Result', verbose_name='Game 2 Submitted'),
        ),
        migrations.AddField(
            model_name='challenge',
            name='loser',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='loser', to='usc_app.Roster', verbose_name='Loser'),
        ),
        migrations.AddField(
            model_name='challenge',
            name='submitted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='submitted_by', to=settings.AUTH_USER_MODEL, verbose_name='Submitted By'),
        ),
        migrations.AddField(
            model_name='challenge',
            name='winner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='winner', to='usc_app.Roster', verbose_name='Winner'),
        ),
        migrations.AddField(
            model_name='roster',
            name='captain',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='captain', to='usc_app.Captain', verbose_name='Captain'),
        ),
        migrations.AddField(
            model_name='captain',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='team', to='usc_app.Roster', verbose_name='Team'),
        ),
    ]
