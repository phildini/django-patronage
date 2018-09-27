from django.db import models
from django.contrib.auth.models import User


class RemoteBenefit(models.Model):

    remote_id = models.CharField(max_length=100, null=True)
    title = models.CharField(max_length=100, null=True)
    url = models.URLField(null=True)

    def __str__(self):
        return self.title


class Tier(models.Model):

    campaign_id = models.CharField(max_length=100, null=True)
    campaign_title = models.CharField(max_length=255, null=True)
    tier_id = models.CharField(max_length=100, null=True)
    tier_title = models.CharField(max_length=100, null=True)
    tier_amount_cents = models.IntegerField(null=True)
    benefits = models.ManyToManyField(RemoteBenefit)
    creators = models.ManyToManyField(User)

    def __str__(self):
        return "{}: {} ({})".format(self.campaign_id, self.tier_title, self.tier_id)


class UserTier(models.Model):

    tier = models.ForeignKey(Tier, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "{} (for {})".format(self.tier, self.user)
