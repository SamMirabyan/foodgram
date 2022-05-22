def delete_recipe(sender, instance, *args, **kwargs):
    """
    Удалить картинку вместе с рецептом.
    """
    instance.image.storage.delete(instance.image.name)
