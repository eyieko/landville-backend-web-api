from rest_framework import serializers
from pages.models import Term


class PagesSerializer(serializers.ModelSerializer):
    """Define whats exposed over the API."""

    class Meta:
        model = Term
        fields = ['details', 'last_updated_at']
