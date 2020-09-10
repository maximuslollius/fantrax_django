from django.db import models


class PlayerNames(models.Model):
    id = models.CharField(primary_key=True, max_length=250)
    name = models.CharField(max_length=250)
    team = models.CharField(max_length=250, blank=True, null=True)
    position = models.CharField(max_length=250, blank=True, null=True)
    position_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name


class PlayerScores(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    team = models.CharField(max_length=250, blank=True, null=True)
    position = models.CharField(max_length=250, blank=True, null=True)
    position_id = models.IntegerField(blank=True, null=True)
    gw_01 = models.FloatField(blank=True, null=True)
    gw_02 = models.FloatField(blank=True, null=True)
    gw_03 = models.FloatField(blank=True, null=True)
    gw_04 = models.FloatField(blank=True, null=True)
    gw_05 = models.FloatField(blank=True, null=True)
    gw_06 = models.FloatField(blank=True, null=True)
    gw_07 = models.FloatField(blank=True, null=True)
    gw_08 = models.FloatField(blank=True, null=True)
    gw_09 = models.FloatField(blank=True, null=True)
    gw_10 = models.FloatField(blank=True, null=True)
    gw_11 = models.FloatField(blank=True, null=True)
    gw_12 = models.FloatField(blank=True, null=True)
    gw_13 = models.FloatField(blank=True, null=True)
    gw_14 = models.FloatField(blank=True, null=True)
    gw_15 = models.FloatField(blank=True, null=True)
    gw_16 = models.FloatField(blank=True, null=True)
    gw_17 = models.FloatField(blank=True, null=True)
    gw_18 = models.FloatField(blank=True, null=True)
    gw_19 = models.FloatField(blank=True, null=True)
    gw_20 = models.FloatField(blank=True, null=True)
    gw_21 = models.FloatField(blank=True, null=True)
    gw_22 = models.FloatField(blank=True, null=True)
    gw_23 = models.FloatField(blank=True, null=True)
    gw_24 = models.FloatField(blank=True, null=True)
    gw_25 = models.FloatField(blank=True, null=True)
    gw_26 = models.FloatField(blank=True, null=True)
    gw_27 = models.FloatField(blank=True, null=True)
    gw_28 = models.FloatField(blank=True, null=True)
    gw_29 = models.FloatField(blank=True, null=True)


class FirstWeekPred(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    pred_01 = models.FloatField(blank=True, null=True)


class PredictedTable(models.Model):
    position = models.IntegerField(blank=True, null=True)
    gw_01 = models.CharField(max_length=250, blank=True, null=True)
    gw_01 = models.CharField(max_length=250, blank=True, null=True)
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

    @property
    def files(self):
        return self.file_set.all()


class SeasonFixtures(models.Model):
    gameweek = models.IntegerField(blank=True, null=True)
    home_team = models.CharField(max_length=250, blank=True, null=True)
    away_team = models.CharField(max_length=250, blank=True, null=True)

    @property
    def files(self):
        return self.file_set.all()
