from django.contrib import admin
from .models import Tier, UserTier, RemoteBenefit

admin.site.register(Tier)
admin.site.register(UserTier)
admin.site.register(RemoteBenefit)
