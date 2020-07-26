from django.dispatch import Signal

# TODO: refactor
user_signed_up = Signal(providing_args=['request', 'user'])