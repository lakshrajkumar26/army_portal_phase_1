from django.db import transaction
from django.apps import apps
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def seed_trades(sender, **kwargs):
    # only run for your app (avoid running for every installed app)
    if sender.name != 'reference':
        return

    Trade = apps.get_model('reference', 'Trade')
    trades = [
        "TTC", "OCC", "DTMN", "EFS", "DMV", "LMN", "CLK SD",
        "STEWARD", "WASHERMAN", "HOUSE KEEPER", "CHEFCOM",
        "MESS KEEPER", "SKT", "Musician", "ARTSN WW", "Hair Dresser", "SP Staff",
    ]

    with transaction.atomic():
        for t in trades:
            Trade.objects.get_or_create(name=t, defaults={"code": t})
