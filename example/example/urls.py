from django.urls import include, path

from .schema import ShemaView


urlpatterns = [
    path('api/', include('multauth.api.urls', namespace='api')),
    path('', ShemaView.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
]
