from django.urls import include, path

# TODO: import based on User._devices
from .email import urls as email_urls
from .phone import urls as phone_urls


urlpatterns = [
    path(r'^', include(email_urls)),
    path(r'^', include(phone_urls)),
]
