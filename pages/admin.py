from django.contrib import admin
from pages.models import Term


class PagesAdmin(admin.ModelAdmin):
    """
    Taps into the Admin functionality of the Pages model.

    Adds some custom behavior to what the LandVille Admin can do
    on the model.

    """

    def has_add_permission(self, request):
        """Ensure the admin cannot create new term Instances."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Ensure the admin cannot delete the existing Term Instance."""
        return False


admin.site.register(Term, PagesAdmin)
