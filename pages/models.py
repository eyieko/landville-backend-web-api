from django.db import models
from ckeditor.fields import RichTextField


class Term(models.Model):
    """Define behaviour and Properties of a Terms and Conditions Instance."""

    details = RichTextField(blank=True, null=True)
    last_updated_at = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Terms and Conditions'
        verbose_name_plural = 'Terms and Conditions'

    def __str__(self):
        return 'Terms and Conditions'
