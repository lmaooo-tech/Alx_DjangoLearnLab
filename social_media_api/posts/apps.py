from django.apps import AppConfig


class PostsConfig(AppConfig):
    """
    Configuration for the posts app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'posts'
    verbose_name = 'Posts'
