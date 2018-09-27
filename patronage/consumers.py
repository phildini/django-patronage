from channels.consumer import SyncConsumer
import requests


class PatreonWebhookConsumer(SyncConsumer):
    def webhook_create(self, message):
        pass
