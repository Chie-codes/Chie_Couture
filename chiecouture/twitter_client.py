import tweepy
from django.conf import settings

# Initialize Tweepy Client (OAuth 2.0 with user context)
client = tweepy.Client(
    consumer_key=settings.X_API_KEY,
    consumer_secret=settings.X_API_KEY_SECRET,
    access_token=settings.X_ACCESS_TOKEN,
    access_token_secret=settings.X_ACCESS_TOKEN_SECRET
)

def tweet_new_store(store_name):
    """
    Post a tweet when a new store is created.
    """
    try:
        response = client.create_tweet(
            text=f"A new store has been added: {store_name}! Check it out now."
        )
        print(f"Tweet sent: {response.data}")
    except Exception as e:
        print(f"Error tweeting new store: {e}")


def tweet_new_product(store_name, product_name):
    """
    Post a tweet when a new product is added to a store.
    """
    try:
        response = client.create_tweet(
            text=f"{store_name} just added a new product: {product_name}! Take a look."
        )
        print(f"Tweet sent: {response.data}")
    except Exception as e:
        print(f"Error tweeting new product: {e}")
