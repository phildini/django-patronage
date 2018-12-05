import logging
import requests

logger = logging.getLogger(__file__)


def get_creator_tiers(patreonuser):
    from .models import Tier

    # TODO: pull tiers on account connect
    logger.info("Getting creator tiers")
    tiers = []
    patreon_response = requests.get(
        "https://www.patreon.com/api/oauth2/v2/campaigns",
        params={
            "include": "tiers,creator",
            "fields[tier]": "title,amount_cents",
            "fields[user]": "full_name",
        },
        headers={"Authorization": "Bearer {}".format(patreonuser.token)},
    )
    patreon_json = patreon_response.json()
    data = patreon_json.get("data")
    if patreon_json.get("included") and data:
        campaign_id = patreon_json.get("data",[{}])[0].get("id")
        creator_id = patreon_json.get("data")[0]["relationships"]["creator"][
            "data"
        ]["id"]
        includes = parse_includes(patreon_json["included"])
        tiers = []
        for tier in includes.get("tier", []):

            tier, created = Tier.objects.get_or_create(
                campaign_id=campaign_id,
                tier_id=tier,
            )
            if created:
                tier.tier_title = includes["tier"][tier].get("attributes", {}).get("title")
                tier.tier_amount_cents = includes["tier"][tier].get("attributes", {}).get("amount_cents")
                tier.campaign_title = includes["user"][creator_id]["attributes"]["full_name"]

            tier.creators.add(patreonuser.account.user)
            tier.save()
            tiers.append(tier)

        tiers = Tier.objects.filter(
            campaign_id=campaign_id,
            creators=patreonuser.account.user,
        ).order_by(
            "tier_amount_cents"
        )
    return tiers


def parse_includes(include_dict):
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
