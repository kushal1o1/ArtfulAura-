from allauth.account.signals import user_signed_up
from django.dispatch import receiver
import requests
from django.db.models.signals import post_save
from .models import Review

@receiver(user_signed_up)
def populate_profile_pic(sociallogin, user, **kwargs):
    if sociallogin.account.provider == 'google':
        data = sociallogin.account.extra_data
        picture_url = data.get('picture')
        if picture_url:
            user.profile_pic = picture_url
            user.save()


@receiver(post_save, sender=Review)
def classify_review_sentiment(sender, instance, created, **kwargs):
    """
    Triggered when a new review is created.
    It sends the review message to the sentiment analysis API, 
    considering if it's a parent review or a reply.
    """
    if created:  # Only run for new reviews
        review_message = instance.message

        # If it's a parent review (not a reply), we send it to the API
        if instance.parent_review is None:
            # Send the review to Hugging Face API for sentiment analysis
            try:
                url = "https://Kushal1o1-review-sentiment-api.hf.space/predict"  # Replace with your Hugging Face model API
                response = requests.get(url, params={"review": review_message})

                # Ensure the response is successful
                if response.status_code == 200:
                    sentiment_data = response.json()
                    print(sentiment_data)
                    sentiment = sentiment_data.get('sentiment', 'Neutral')

                    # Update the review object with the sentiment
                    instance.sentiment = sentiment
                    instance.save()

                else:
                    print(f"Error from sentiment API: {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"Error connecting to sentiment API: {e}")

        else:
            # If it's a reply (parent review exists), we could use the parent's sentiment
            parent_review = instance.parent_review
            if parent_review.sentiment:
                # If the parent review already has a sentiment, we can just inherit it
                instance.sentiment = parent_review.sentiment
                instance.save()

            # Optionally, if you'd prefer to send the reply for sentiment analysis too, you can uncomment the following:
            else:
                try:
                    url = "https://Kushal1o1-review-sentiment-api.hf.space/predict"  # Replace with your Hugging Face model API
                    response = requests.get(url, params={"review": review_message})
            
                    if response.status_code == 200:
                        sentiment_data = response.json()
                        sentiment = sentiment_data.get('sentiment', 'Neutral')
            
                        # Update the review object with the sentiment
                        instance.sentiment = sentiment
                        instance.save()
            
                    else:
                        print(f"Error from sentiment API: {response.status_code}")
            
                except requests.exceptions.RequestException as e:
                    print(f"Error connecting to sentiment API: {e}")