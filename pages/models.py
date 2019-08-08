from django.db import models
from ckeditor.fields import RichTextField
# Create your models here.


class Term(models.Model):
    details = RichTextField(blank=True, null=True)
    last_updated_at = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Terms and Conditions'
        verbose_name_plural = 'Terms and Conditions'

    def __str__(self):
        return 'Terms and Conditions'
