from django.contrib import admin

from django.urls import include, path
from django.views.generic import TemplateView

import multauth

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', TemplateView.as_view(template_name='index.html')),

    path('api/', include('multauth.api.urls', namespace='api')),

    path('403/', TemplateView.as_view(template_name='403.html')),
    path('500/', TemplateView.as_view(template_name='500.html')),
]


handler403 = 'views.handler403'
handler404 = 'views.handler404'
handler500 = 'views.handler500'
