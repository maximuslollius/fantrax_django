from django.db import models
from django.template.defaultfilters import slugify


class PlayerScoresMinutes(models.Model):
    id = models.CharField(primary_key=True, max_length=250)
    player = models.CharField(max_length=250)
    team = models.CharField(max_length=250, blank=True, null=True)
    position = models.CharField(max_length=250, blank=True, null=True)
    position_id = models.IntegerField(blank=True, null=True)
    date = models.CharField(max_length=250, blank=True, null=True)
    opposition = models.CharField(max_length=250, blank=True, null=True)
    result = models.CharField(max_length=250, blank=True, null=True)
    FPts = models.IntegerField(blank=True, null=True)
    minutes = models.IntegerField(blank=True, null=True)
    season = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.player


class ScoreDistribution(models.Model):
    id = models.CharField(primary_key=True, max_length=250)
    minutes_played = models.IntegerField(blank=True, null=True)
    actual_score = models.IntegerField(default=0)
    extrap_score = models.IntegerField(default=0)

    def __str__(self):
        return self.id


class PlayerNames(models.Model):
    id = models.CharField(primary_key=True, max_length=250)
    name = models.CharField(max_length=250)
    slug = models.SlugField(null=True, blank=True)
    team = models.CharField(max_length=250, blank=True, null=True)
    position = models.CharField(max_length=250, blank=True, null=True)
    position_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)

        super(PlayerNames, self).save(*args, **kwargs)


class SeasonFixtures(models.Model):
    id = models.CharField(primary_key=True, max_length=250)
    gw = models.IntegerField(blank=True, null=True)
    act_gw = models.IntegerField(blank=True, null=True)
    game_order = models.IntegerField(blank=True, null=True)
    act_game_order = models.IntegerField(blank=True, null=True)
    home_team = models.CharField(max_length=250, blank=True, null=True)
    away_team = models.CharField(max_length=250, blank=True, null=True)
    home_pct = models.CharField(max_length=250, blank=True, null=True)
    away_pct = models.CharField(max_length=250, blank=True, null=True)
    link = models.CharField(max_length=250, blank=True, null=True)
    home_formation = models.CharField(max_length=250, blank=True, null=True)
    away_formation = models.CharField(max_length=250, blank=True, null=True)


class InitialConditions(models.Model):
    id = models.CharField(primary_key=True, max_length=250)
    player = models.CharField(max_length=250, blank=True, null=True)
    initial_condition = models.FloatField(blank=True, null=True)
    club_position_id = models.IntegerField(blank=True, null=True)


class NormScores(models.Model):
    name = models.CharField(max_length=250)
    team = models.CharField(max_length=250, blank=True, null=True)
    position = models.CharField(max_length=250, blank=True, null=True)
    position_id = models.IntegerField(blank=True, null=True)
    pre_01 = models.CharField(max_length=250, blank=True, null=True)
    gw_01 = models.CharField(max_length=250, blank=True, null=True)
    gw_02 = models.CharField(max_length=250, blank=True, null=True)
    gw_03 = models.CharField(max_length=250, blank=True, null=True)
    gw_04 = models.CharField(max_length=250, blank=True, null=True)
    gw_05 = models.CharField(max_length=250, blank=True, null=True)
    gw_06 = models.CharField(max_length=250, blank=True, null=True)
    gw_07 = models.CharField(max_length=250, blank=True, null=True)
    gw_08 = models.CharField(max_length=250, blank=True, null=True)
    gw_09 = models.CharField(max_length=250, blank=True, null=True)
    gw_10 = models.CharField(max_length=250, blank=True, null=True)
    gw_11 = models.CharField(max_length=250, blank=True, null=True)
    gw_12 = models.CharField(max_length=250, blank=True, null=True)
    gw_13 = models.CharField(max_length=250, blank=True, null=True)
    gw_14 = models.CharField(max_length=250, blank=True, null=True)
    gw_15 = models.CharField(max_length=250, blank=True, null=True)
    gw_16 = models.CharField(max_length=250, blank=True, null=True)
    gw_17 = models.CharField(max_length=250, blank=True, null=True)
    gw_18 = models.CharField(max_length=250, blank=True, null=True)
    gw_19 = models.CharField(max_length=250, blank=True, null=True)
    gw_20 = models.CharField(max_length=250, blank=True, null=True)
    gw_21 = models.CharField(max_length=250, blank=True, null=True)
    gw_22 = models.CharField(max_length=250, blank=True, null=True)
    gw_23 = models.CharField(max_length=250, blank=True, null=True)
    gw_24 = models.CharField(max_length=250, blank=True, null=True)
    gw_25 = models.CharField(max_length=250, blank=True, null=True)
    gw_26 = models.CharField(max_length=250, blank=True, null=True)
    gw_27 = models.CharField(max_length=250, blank=True, null=True)
    gw_28 = models.CharField(max_length=250, blank=True, null=True)
    gw_29 = models.CharField(max_length=250, blank=True, null=True)
    gw_30 = models.CharField(max_length=250, blank=True, null=True)
    gw_31 = models.CharField(max_length=250, blank=True, null=True)
    gw_32 = models.CharField(max_length=250, blank=True, null=True)
    gw_33 = models.CharField(max_length=250, blank=True, null=True)
    gw_34 = models.CharField(max_length=250, blank=True, null=True)
    gw_35 = models.CharField(max_length=250, blank=True, null=True)
    gw_36 = models.CharField(max_length=250, blank=True, null=True)
    gw_37 = models.CharField(max_length=250, blank=True, null=True)
    gw_38 = models.CharField(max_length=250, blank=True, null=True)

    @property
    def files(self):
        return self.file_set.all()


class PlayerProfileScores(models.Model):
    gw = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=250)
    field_pos = models.CharField(max_length=250, blank=True, null=True)
    team = models.CharField(max_length=250, blank=True, null=True)
    opp = models.CharField(max_length=250, blank=True, null=True)
    start = models.IntegerField(blank=True, null=True)
    min = models.IntegerField(blank=True, null=True)
    fpts = models.CharField(max_length=250, blank=True, null=True)
    normscore = models.CharField(max_length=250, blank=True, null=True)
    ownership = models.CharField(max_length=250, blank=True, null=True)

    @property
    def files(self):
        return self.file_set.all()


class SingleFixture(models.Model):
    id = models.CharField(max_length=250, primary_key=True)
    fixture_id = models.CharField(max_length=250)
    slug = models.SlugField(null=True, blank=True)
    formation_1 = models.CharField(max_length=250, blank=True, null=True)
    formation_2 = models.CharField(max_length=250, blank=True, null=True)
    starter_H_I = models.CharField(max_length=250, blank=True, null=True)
    starter_H_II = models.CharField(max_length=250, blank=True, null=True)
    starter_H_III = models.CharField(max_length=250, blank=True, null=True)
    starter_H_IV = models.CharField(max_length=250, blank=True, null=True)
    starter_H_V = models.CharField(max_length=250, blank=True, null=True)
    starter_H_VI = models.CharField(max_length=250, blank=True, null=True)
    starter_H_VII = models.CharField(max_length=250, blank=True, null=True)
    starter_H_VIII = models.CharField(max_length=250, blank=True, null=True)
    starter_H_IX = models.CharField(max_length=250, blank=True, null=True)
    starter_H_X = models.CharField(max_length=250, blank=True, null=True)
    starter_H_XI = models.CharField(max_length=250, blank=True, null=True)
    starter_A_I = models.CharField(max_length=250, blank=True, null=True)
    starter_A_II = models.CharField(max_length=250, blank=True, null=True)
    starter_A_III = models.CharField(max_length=250, blank=True, null=True)
    starter_A_IV = models.CharField(max_length=250, blank=True, null=True)
    starter_A_V = models.CharField(max_length=250, blank=True, null=True)
    starter_A_VI = models.CharField(max_length=250, blank=True, null=True)
    starter_A_VII = models.CharField(max_length=250, blank=True, null=True)
    starter_A_VIII = models.CharField(max_length=250, blank=True, null=True)
    starter_A_IX = models.CharField(max_length=250, blank=True, null=True)
    starter_A_X = models.CharField(max_length=250, blank=True, null=True)
    starter_A_XI = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.fixture_id

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.fixture_id)

        super(SingleFixture, self).save(*args, **kwargs)
