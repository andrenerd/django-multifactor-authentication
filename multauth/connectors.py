from django.db.models.signals import m2m_changed
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.apps import apps


# RESERVED # not possible as the "request" object is not accessible
# @receiver(pre_save, sender=get_user_model())
# def user_pre_save(sender, instance, **kwargs):
#     user = instance

#     if user.pk:
#         user_old = get_user_model().objects.get(pk=user.pk)

#         if user.email and user.email is not user_old.email:
#             user.verify_email(request)

#         if user.phone and user.phone is not user_old.phone:
#             user.verify_phone(request)


@receiver(m2m_changed)
def create_profiles(sender, instance, model, pk_set, action, **kwargs):
    """
    Create custom profiles (CustomUser, ...)
    for users added to related groups
    """
    if isinstance(instance, Group) and issubclass(model, get_user_model()):
        if action in ['post_add',]:
            group_name = instance.name
            profile_name = get_user_model().PROFILES.get(group_name)
            profile_cls = apps.get_model(**profile_name)

            if profile_cls:
                for pk in pk_set:
                    user = get_user_model().objects.get(pk=pk)
                    group_profile = profile_cls.objects.get_or_create(user=user)

    else:
        # it's not a m2m signal we are interested in
        return
