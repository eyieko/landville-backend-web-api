from django.utils.text import slugify


def generate_unique_slug(model_instance, slug_field_name):
    """
    We will take a property instance then generate a slug for it.
    If the property instance has an address that contains a street, we
    will slugify the street name and title, incrementing by 1 if the resulting
    slug is not unique.

    """
    address = getattr(model_instance, 'address')
    title = getattr(model_instance, 'title')

    street = address.get('Street')

    if street is not None:
        slug_text = f'{street} {title}'
    else:
        slug_text = f'{title}'

    slug = slugify(slug_text)
    unique_slug = slug
    extension = 1
    ModelClass = model_instance.__class__

    while ModelClass._default_manager.filter(
        **{slug_field_name: unique_slug}
    ).exists():
        unique_slug = '{}-{}'.format(slug, extension)
        extension += 1

    return unique_slug
