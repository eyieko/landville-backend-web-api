from django.shortcuts import render
from rest_framework.views import APIView
from .models import Term
from .serializers import PagesSerializer
from rest_framework.response import Response
# Create your views here.


class TermsView(APIView):
    serializer_class = PagesSerializer

    def get(self, request, format=None):
        terms = Term.objects.all()
        serializer = PagesSerializer(terms, many=True)
        return Response(serializer.data)
