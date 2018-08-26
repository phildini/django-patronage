import logging
import requests

logger = logging.getLogger(__file__)


def get_creator_tiers(patreonuser):
    from .models import Benefit
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
    if patreon_json.get("included"):
        includes = parse_includes(patreon_json["included"])
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