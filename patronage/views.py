import logging
import requests
from django.views.generic import TemplateView

from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialToken, SocialApp

from django.utils.crypto import get_random_string

from .models import Benefit

from django.shortcuts import get_object_or_404, redirect

logger = logging.getLogger(__file__)


class PatronageView(TemplateView):

    template_name = "patronage.html"

    def create_remote_benefit(self):
        return None, None

    def post(self, request, *args, **kwargs):
        post_data = request.POST.copy()
        benefits = []
        for tier in post_data:
            try:
                if post_data[tier] == "on":
                    benefits.append(
                        Benefit.objects.get(tier_id=int(tier), remote_benefit_id=None)
                    )
            except Benefit.DoesNotExist:
                pass
        if benefits:
            remote_benefit_id, remote_benefit_title = self.create_remote_benefit()
        for benefit in benefits:
            benefit.remote_benefit_id = remote_benefit_id
            benefit.remote_benefit_title = remote_benefit_title
            benefit.save()
        return redirect("/")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        self.patreonuser = None
        context["process"] = "login"
        if self.request.user.is_authenticated:
            context["process"] = "connect"
            try:
                self.patreonuser = SocialToken.objects.get(
                    account__user=self.request.user, app__provider="patreon"
                )
            except SocialToken.DoesNotExist:
                pass
            if self.patreonuser:
                context["creator_tiers"] = self.get_creator_tiers()
                context["patron_tiers"] = self.get_patron_tiers()
        return context

    def get_creator_tiers(self):
        # TODO: pull tiers on account connect
        logger.info("Getting creator tiers")
        tiers = []
        r = requests.get(
            "https://www.patreon.com/api/oauth2/v2/campaigns",
            params={
                "include": "tiers,creator",
                "fields[tier]": "title,amount_cents",
                "fields[user]": "full_name",
            },
            headers={"Authorization": "Bearer {}".format(self.patreonuser.token)},
        )
        patreon_json = r.json()
        if patreon_json.get("included"):
            includes = self.parse_includes(patreon_json["included"])
            tiers = []
            for tier in includes["tier"]:
                campaign_id = patreon_json.get("data")[0].get("id")
                creator_id = patreon_json.get("data")[0]["relationships"]["creator"][
                    "data"
                ]["id"]
                benefit, created = Benefit.objects.get_or_create(
                    campaign_id=campaign_id,
                    campaign_title=includes["user"][creator_id]["attributes"][
                        "full_name"
                    ],
                    tier_id=tier,
                    tier_title=includes["tier"][tier]
                    .get("attributes", {})
                    .get("title"),
                    tier_amount_cents=includes["tier"][tier]
                    .get("attributes", {})
                    .get("amount_cents"),
                )
                tiers.append(benefit)

            tiers = Benefit.objects.filter(campaign_id=campaign_id).order_by(
                "tier_amount_cents"
            )
        return tiers

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
        patron_benefits = []
        if patron_json.get("included"):
            includes = self.parse_includes(patron_json["included"])
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
                    benefit, _ = Benefit.objects.get_or_create(
                        campaign_id=campaign_id,
                        campaign_title=includes["user"][creator_id]["attributes"][
                            "full_name"
                        ],
                        tier_id=tier["id"],
                        tier_title=includes["tier"][tier["id"]]["attributes"]["title"],
                    )
                    patron_benefits.append(benefit)
        return patron_benefits

    def parse_includes(self, include_dict):
        includes = {}
        for include in include_dict:
            include_dict = {
                "attributes": include["attributes"],
                "relationships": include.get("relationships", {}),
            }
            id = include["id"]
            if include["type"] not in includes:
                includes[include["type"]] = {id: include_dict}
            else:
                includes[include["type"]][id] = include_dict

        return includes
