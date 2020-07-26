"""
Decorators to handle authentication (and other) wrappers for views.

- is_authenticated
- is_custom_user
- ...
"""

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def is_authenticated(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that
    limit access to "authenticated users" only
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated(),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )

    if function:
        return actual_decorator(function)
    return actual_decorator


def is_admin(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that
    limit access to "authenticated admin users" only
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and u.is_admin,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )

    if function:
        return actual_decorator(function)
    return actual_decorator


# EXAMPLE
# def is_custom_user(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
#     """
#     Decorator for views that
#     limit access to "authenticated custom users" only
#     """
#     actual_decorator = user_passes_test(
#         lambda u: u.is_authenticated() and u.is_custom_user,
#         login_url=login_url,
#         redirect_field_name=redirect_field_name
#     )

#     if function:
#         return actual_decorator(function)
#     return actual_decorator
