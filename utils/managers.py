from django.db.models import QuerySet


class CustomQuerySet(QuerySet):
    """Custom queryset that will be reused by different models. It enables soft delete and precise filtering"""

    def _active(self):
        """Return only objects that haven't been soft deleted"""
        return self.filter(is_deleted=False)

    def all_objects(self):
        """Return all objects that haven't been soft deleted"""
        return self._active()


class PropertyQuery(CustomQuerySet):
    """Queryset that will be used by the property model"""

    def all_property_for_client(self, client):
        return self._active().filter(client=client)
