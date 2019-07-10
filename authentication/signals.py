from django.db.models.signals import post_save
from authentication.models import User, UserProfile
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.userprofile.save()


class SocialAuthProfileUpdate:
    """
    This class holds the signals responsible for extracting the 
    user information from the token and updating the user's profile
    """
    @staticmethod
    def profile(user_info):
        """
        Uses information from the facebook token to update a usersprofile
        params: user info(a dictionary with user information from a token)
        returns: function that implements profile update
        """
        def update_profile(sender, instance, **kwargs):
            """
            Updates profile of the current user basing on information
            from the user token
            params: sender - object that is sending a signal
                    instance - the current object
            returns: n/a
            """
            # get the generated profile of the current facebook user
            profile = UserProfile.objects.get(user=instance)

            social_pic = user_info.get('user_profile_picture')
            # check if the user has a profile

            if social_pic:
                # update profile image(avator)
                profile.image = social_pic
                profile.save()

        return update_profile

    @staticmethod
    def get_user_info(user_info):
        """
        Get the current url
        """
        post_save.connect(SocialAuthProfileUpdate.profile(
            user_info), sender=User, weak=False)
