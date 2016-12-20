# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-12-18 19:57
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('played', models.BooleanField(default=False, verbose_name='Played?')),
                ('map', models.CharField(max_length=50, verbose_name='Map')),
                ('challenge_date', models.DateField(default=datetime.date.today, verbose_name='Challenge Date')),
                ('forfeit_date', models.DateField(default=datetime.date(2016, 12, 23), verbose_name='Forfeit Date')),
                ('void_date', models.DateField(default=datetime.date(2017, 1, 1), verbose_name='Void Date')),
                ('play_date', models.DateField(blank=True, null=True, verbose_name='Date Played')),
            ],
            options={
                'db_table': 'challenges',
            },
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('minutes', models.PositiveIntegerField(blank=True, null=True)),
                ('tags', models.PositiveIntegerField(blank=True, null=True)),
                ('captures', models.PositiveIntegerField(blank=True, null=True)),
                ('hold', models.CharField(blank=True, max_length=10, null=True)),
                ('returns', models.PositiveIntegerField(blank=True, null=True)),
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
                ('score1', models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Score 1')),
                ('score2', models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Score 2')),
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
                ('firstActive', models.CharField(max_length=50)),
                ('daysActive', models.PositiveIntegerField()),
                ('server', models.CharField(max_length=50)),
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
                ('rank', models.IntegerField(default=0)),
                ('streak', models.IntegerField(blank=True, default=0, null=True)),
                ('highestRank', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('uscmRank', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('lastActive', models.CharField(blank=True, max_length=50)),
                ('challengeOut', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('challengeIn', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('GP', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('W', models.IntegerField(blank=True, default=0, null=True)),
                ('L', models.IntegerField(blank=True, default=0, null=True)),
                ('D', models.IntegerField(blank=True, default=0, null=True)),
                ('F', models.IntegerField(blank=True, default=0, null=True)),
                ('CF', models.IntegerField(blank=True, default=0, null=True)),
                ('CA', models.IntegerField(blank=True, default=0, null=True)),
                ('CD', models.IntegerField(blank=True, default=0, null=True)),
                ('CDperG', models.IntegerField(blank=True, default=0, null=True, verbose_name='CD/G')),
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
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='co_captain', to='usc_app.Player', verbose_name='Co-Captain'),
        ),
        migrations.AddField(
            model_name='roster',
            name='member1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member1', to='usc_app.Player', verbose_name='Member1'),
        ),
        migrations.AddField(
            model_name='roster',
            name='member2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member2', to='usc_app.Player', verbose_name='Member2'),
        ),
        migrations.AddField(
            model_name='roster',
            name='member3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member3', to='usc_app.Player', verbose_name='Member3'),
        ),
        migrations.AddField(
            model_name='roster',
            name='member4',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member4', to='usc_app.Player', verbose_name='Member4'),
        ),
        migrations.AddField(
            model_name='roster',
            name='member5',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member5', to='usc_app.Player', verbose_name='Member5'),
        ),
        migrations.AddField(
            model_name='roster',
            name='member6',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member6', to='usc_app.Player', verbose_name='Member6'),
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
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='g1_results', to='usc_app.Result', verbose_name='Game 1 Results'),
        ),
        migrations.AddField(
            model_name='challenge',
            name='g2_results',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='g2_results', to='usc_app.Result', verbose_name='Game 2 Results'),
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
        migrations.AddField(
            model_name='captain',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
