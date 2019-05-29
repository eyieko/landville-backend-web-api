from django.db.models import QuerySet, Q


class CustomQuerySet(QuerySet):
    """
    Custom queryset that will be reused by different models.
    It enables soft delete and precise filtering, (ie to get all
    property that has not been soft deleted, simply run:
        Property.active_objects.all_objects()
        )
    """

    def _active(self):
        """Return only objects that haven't been soft deleted."""
        return self.filter(is_deleted=False)

    def all_objects(self):
        """Return all objects that haven't been soft deleted"""
        return self._active()


class PropertyQuery(CustomQuerySet):
    """Queryset that will be used by the property model"""

    def for_client(self, client):
        """This query set returns all property that belongs to a client, whether published or not"""
        return self._active().filter(client=client)

    def by_slug(self, slug):
        """Return property with the passed slug"""
        return self._active().filter(slug=slug)

    def all_published(self):
        """Returns all property that is published"""
        return self._active().filter(is_published=True)

    def all_sold(self):
        """Return all property that is sold"""
        return self._active().filter(is_sold=True)

    def all_published_and_all_by_client(self, client):
        """Return all property that are published and also all property owned by the client"""
        return self._active().filter(Q(is_published=True)) | self._active().filter(Q(client=client))


class ClientAccountQuery(CustomQuerySet):
    """ Queryset that will be used for ClientAccount model"""

    def not_deleted(self, owner):
        """ return client details that are not deleted """
        return self._active().filter(owner=owner)

    def client_admin_has_client(self, client_admin_id):
        """check if client Admin has an Client Account if not do not enable him/her to submit account details"""
        return self._active().filter(client_admin_id=id)
