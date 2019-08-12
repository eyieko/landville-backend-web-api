from django.contrib import admin
from pages.models import Term


class PagesAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# Register your models here.
admin.site.register(Term, PagesAdmin)
