from django.db import models


class Benefit(models.Model):

    campaign_id = models.CharField(max_length=100, null=True)
    campaign_title = models.CharField(max_length=255, null=True)
    tier_id = models.CharField(max_length=100, null=True)
    tier_title = models.CharField(max_length=100, null=True)
    tier_amount_cents = models.IntegerField(null=True)
    remote_benefit_id = models.CharField(max_length=100, null=True)
    remote_benefit_title = models.CharField(max_length=100, null=True)

    def __str__(self):
        return "{}: {} ({})".format(self.campaign_id, self.tier_title, self.tier_id)