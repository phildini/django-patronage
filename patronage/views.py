import logging
import requests
from django.views.generic import TemplateView

from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialApp, SocialToken, SocialAccount

from django.utils.crypto import get_random_string

from .models import Tier, UserTier, RemoteBenefit
from .util import get_creator_tiers, parse_includes

from django.shortcuts import get_object_or_404, redirect

logger = logging.getLogger(__file__)


class PatronageView(TemplateView):
    remote_app = 'remote_app'
    remote_app_name = 'RemoteAppName'
    template_name = "patronage.html"

    def create_remote_benefit(self):
        return None, None

    def grant_remote_benefits(self, tier):
        pass

    def get_remote_benefits(self):
        return None

    def post(self, request, *args, **kwargs):
        post_data = request.POST.copy()
        tiers = {
            tier.lstrip("tier--"): post_data[tier]
            for tier in post_data.keys()
            if tier.startswith("tier--")
        }
        benefits = [
            benefit.lstrip("benefit--")
            for benefit in post_data.keys()
            if benefit.startswith("benefit--") and post_data[benefit] == "on"
        ]
        benefits = RemoteBenefit.objects.filter(id__in=benefits)
        for tier, value in tiers.items():
            if value == "on":
                tier = Tier.objects.get(tier_id=int(tier))
                tier.benefits.add(*list(benefits))
                tier.save()
                self.grant_remote_benefits(tier)
        return redirect("/")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        self.patreonuser = None
        if self.remote_app:
            context["remote_app"] = self.remote_app
            context["remote_app_name"] = self.remote_app_name
        context["process"] = "login"
        if self.request.user.is_authenticated:
            context["process"] = "connect"
            try:
                self.patreonuser = SocialToken.objects.get(
                    account__user=self.request.user, app__provider="patreon"
                )
                context["remote_user"] = SocialToken.objects.get(
                    account__user=self.request.user, app__provider=self.remote_app
                )
            except SocialToken.DoesNotExist:
                pass
            if self.patreonuser:
                context["creator_tiers"] = get_creator_tiers(self.patreonuser)
                context["patron_tiers"] = self.get_patron_tiers()
                context["remote_benefits"] = self.get_remote_benefits()
        context["patreonuser"] = self.patreonuser
        return context

    def get_patron_tiers(self):
        logger.info("getting patron tiers")
        response = requests.get(
            "https://www.patreon.com/api/oauth2/v2/identity",
            params={
                "include": "memberships,memberships.currently_entitled_tiers,memberships.campaign.creator",
                "fields[tier]": "title",
                "fields[user]": "full_name",
            },
            headers={"Authorization": "Bearer {}".format(self.patreonuser.token)},
        )
        patron_json = response.json()
        if patron_json.get("included"):
            includes = parse_includes(patron_json["included"])
            memberships = [
                member
                for member in patron_json["included"]
                if member["type"] == "member"
            ]
            for membership in memberships:
                campaign = (
                    membership.get("relationships", {})
                    .get("campaign", {})
                    .get("data", {})
                )
                campaign_id = campaign.get("id")
                creator_id = includes["campaign"][campaign_id]["relationships"][
                    "creator"
                ]["data"]["id"]
                campaign_title = campaign.get("attributes", {}).get("summary")
                patron_tiers = (
                    membership.get("relationships", {})
                    .get("currently_entitled_tiers", {})
                    .get("data")
                )
                if patron_tiers:
                    tier = patron_tiers[0]
                    tier, _ = Tier.objects.get_or_create(
                        campaign_id=campaign_id,
                        campaign_title=includes["user"][creator_id]["attributes"][
                            "full_name"
                        ],
                        tier_id=tier["id"],
                        tier_title=includes["tier"][tier["id"]]["attributes"]["title"],
                    )
                    userbenefit, _ = UserTier.objects.get_or_create(
                        user=self.request.user, tier=tier
                    )
                    self.grant_remote_benefits(tier)
        return Tier.objects.filter(usertier__user=self.request.user).exclude(benefits=None)
