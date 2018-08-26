from django.apps import AppConfig
from django.dispatch import receiver
from allauth.socialaccount import signals

from .util import get_creator_tiers

def social_account_signal_handler(sender, **kwargs):
    from allauth.socialaccount.models import SocialToken
    sociallogin = kwargs.get('sociallogin')
    if sociallogin and sociallogin.account.provider == 'patreon':
        try:
            patreonuser = SocialToken.objects.get(
                account__user=sociallogin.account.user, app__provider="patreon"
            )
            tiers = get_creator_tiers(patreonuser)
        except SocialToken.DoesNotExist:
            pass


class PatronageConfig(AppConfig):
    name = "patronage"

    def ready(self):
        signals.social_account_added.connect(social_account_signal_handler)
        signals.social_account_updated.connect(social_account_signal_handler)

