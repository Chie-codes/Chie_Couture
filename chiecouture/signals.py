from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Store, Product
from .twitter_client import tweet_new_store, tweet_new_product


@receiver(post_save, sender=Store)
def announce_new_store(sender, instance, created, **kwargs):
    """
    Post a tweet when a new store is created.
    """
    if created:  # only tweet for new stores
        try:
            tweet_new_store(instance.name)
        except Exception as e:
            print(f"Error tweeting about new store: {e}")


@receiver(post_save, sender=Product)
def announce_new_product(sender, instance, created, **kwargs):
    """
    Post a tweet when a new product is created.
    """
    if created:  # only tweet for new products
        try:
            tweet_new_product(instance.store.name, instance.name)
        except Exception as e:
            print(f"Error tweeting about new product: {e}")
