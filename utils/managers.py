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

    def all_approved(self):
        """ return client companies that are approved"""
        return self._active().filter(approval_status='approved')


class PropertyQuery(CustomQuerySet):
    """Queryset that will be used by the property model"""

    def for_client(self, client):
        """This query set returns all property that
           belongs to a client, whether published or not"""
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

    def all_published_and_all_not_sold(self):
        """ returns all published and unsold properties """
        return self._active().filter(Q(is_published=True)) and self._active(
        ).filter(Q(is_sold=False))

    def published_and_unsold_property_by_slug(self, slug):
        """
        using a slug, return a property that is both unsold and unpublished
        """
        return self.all_published_and_all_not_sold().filter(slug=slug)

    def all_published_and_all_by_client(self, client):
        """
        Return all property that are published and also all
        property owned by the client
        """
        return self._active().filter(Q(is_published=True)) | self._active(
        ).filter(Q(client=client))


class PropertyEnquiryQuery(CustomQuerySet):
    """ Queryset for the Enquiry property """

    def for_user(self, user):
        """ returns all the queries made by a buyer """
        return self._active().filter(requester=user)

    def for_client(self, client):
        """ return all the queires made for a certain client """
        return self._active().filter(client=client)


class ClientAccountQuery(CustomQuerySet):
    """ Queryset that will be used for ClientAccount model"""

    def not_deleted(self, owner):
        """ return client details that are not deleted """
        return self._active().filter(owner=owner)

    def client_admin_has_client(self, client_admin_id):
        """check if client Admin has an Client Account
        if not do not enable him/her to submit account details"""
        return self._active().filter(owner_id=client_admin_id)
