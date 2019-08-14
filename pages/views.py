from rest_framework.views import APIView
from pages.models import Term
from pages.serializers import PagesSerializer
from rest_framework.response import Response
from rest_framework import status


class TermsView(APIView):
    """Handles sending terms and conditions to users."""

    serializer_class = PagesSerializer

    def get(self, request):
        """Query for terms of use and serve them over http."""
        terms = Term.objects.latest('last_updated_at')
        serializer = PagesSerializer(terms)
        return Response(serializer.data, status=status.HTTP_200_OK)
