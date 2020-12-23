from django.contrib import admin

from django.urls import include, path


urlpatterns = [
    path('', include('multauth.api.urls', namespace='api')),
]
