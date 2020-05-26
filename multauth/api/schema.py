from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi


ShemaView = get_schema_view(
   openapi.Info(
      title='Multauth API',
      default_version='v1',
      description='Draft',
      # terms_of_service="https://www.google.com/policies/terms/",
      # contact=openapi.Contact(email="contact@snippets.local"),
      # license=openapi.License(name="MIT"),
   ),
   #validators=['flex', 'ssv'],
   public=True,
   permission_classes=(permissions.AllowAny,),
)
