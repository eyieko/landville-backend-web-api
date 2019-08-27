from django import forms
from django.contrib import (
    admin,
    messages,
)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from authentication.models import User, Client, UserProfile, ClientReview
from django.http import HttpResponseRedirect
from utils.tasks import send_email_notification


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password',
                  'is_active', 'is_superuser', 'role', 'username')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial.get('password')


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'is_superuser', 'first_name', 'last_name')
    list_filter = ('created_at', 'is_superuser',)
    fieldsets = (
        (None, {'fields': ('password',)}),
        ('Personal info', {
         'fields': ('email', 'first_name', 'last_name', 'username')}),
        ('Permissions', {
         'fields': (
             'is_superuser',
             'is_staff',
             'groups',
             'user_permissions')}),
        ('User Roles', {
            'fields': ('is_active', 'role', 'is_verified')
        }),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name',
                       'password1', 'password2'
                       )}
         ),
    )
    search_fields = ('email', 'first_name', 'last_name', 'username'),
    list_per_page = 15
    ordering = ('email',)
    filter_horizontal = ()


# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
# ... and, since we're not using Django's built-in permissions,


class ClientAdmin(admin.ModelAdmin):
    """This class adds custom behavior to the Client ModelAdmin.

    Enable overriding of the response_post_save_change method.
    """

    list_display = ("client_name", "client_admin",
                    "phone", "email", "approval_status")
    ordering = ["-created_at"]

    def response_post_save_change(self, request, obj):
        """
        Figure out where to redirect after the 'Save' button has been pressed
        when editing an existing object.
        """
        if obj.approval_status == 'approved':
            message = "Hey there,\n\nyour application was accepted, you may " \
                      "now start listing property"
            payload = {
                "subject": "LandVille Application Status",
                "recipient": [obj.client_admin.email],
                "text_body": "email/authentication/base_email.txt",
                "html_body": "email/authentication/base_email.html",
                "context": {
                    'title': "Hey there,",
                    'message': message
                }
            }
            send_email_notification.delay(payload)
            return self._response_post_save(request, obj)
        else:
            messages.info(request,
                          message="Please add a reason for your action in "
                                  "the text box below")
            return HttpResponseRedirect(
                "/api/v1/auth/admin/notes/?status={}&client={}".format(
                    obj.approval_status, obj.client_admin.email))


admin.site.register(Client, ClientAdmin)
admin.site.register(UserProfile)
admin.site.register(ClientReview)
