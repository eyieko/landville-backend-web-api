from rest_framework import serializers
from .models import Term


class PagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = ['details', 'last_updated_at']