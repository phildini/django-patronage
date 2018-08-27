import logging
import requests
from django.views.generic import TemplateView

from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialToken

from django.utils.crypto import get_random_string

from .models import Benefit, UserBenefit
from .util import get_creator_tiers, parse_includes

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
                context["creator_tiers"] = get_creator_tiers(self.patreonuser)
                context["patron_tiers"] = self.get_patron_tiers()
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
        patron_benefits = []
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
                    benefit, _ = Benefit.objects.get_or_create(
                        campaign_id=campaign_id,
                        campaign_title=includes["user"][creator_id]["attributes"][
                            "full_name"
                        ],
                        tier_id=tier["id"],
                        tier_title=includes["tier"][tier["id"]]["attributes"]["title"],
                    )
                    userbenefit, _ = UserBenefit.objects.get_or_create(
                        user=self.request.user,
                        benefit=benefit,
                    )
                    patron_benefits.append(benefit)
        return patron_benefits
