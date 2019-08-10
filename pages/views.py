from rest_framework.views import APIView
from .models import Term
from .serializers import PagesSerializer
from rest_framework.response import Response


class TermsView(APIView):
    serializer_class = PagesSerializer

    def get(self, request):
        terms = Term.objects.latest('last_updated_at')
        serializer = PagesSerializer(terms)
        return Response(serializer.data)
