from allauth.account.signals import user_signed_up
from django.dispatch import receiver

@receiver(user_signed_up)
def populate_profile_pic(sociallogin, user, **kwargs):
    if sociallogin.account.provider == 'google':
        data = sociallogin.account.extra_data
        picture_url = data.get('picture')
        if picture_url:
            user.profile_pic = picture_url
            user.save()
