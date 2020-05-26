from rest_framework import views
from rest_framework.response import Response


class IndexView(views.APIView):
    def get(self, request, format=None):
        return Response('Welcome to API')
