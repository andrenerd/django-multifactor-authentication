from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi


ShemaView = get_schema_view(
   openapi.Info(
      title='Multauth Example API',
      default_version='v1',
      description='Authentication flow: email, password and passcode (using Google Authenticator or similar app)',
      # terms_of_service="https://www.google.com/policies/terms/",
      # contact=openapi.Contact(email="contact@snippets.local"),
      # license=openapi.License(name="BSD License"),
   ),
   #validators=['flex', 'ssv'],
   public=True,
   permission_classes=(permissions.AllowAny,),
)
