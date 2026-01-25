from django.apps import AppConfig
from django.db.models.signals import post_migrate


class RelationshipAppConfig(AppConfig):
    name = 'relationship_app'

    def ready(self):
        """Ensure default groups with permissions exist after migrations."""
        post_migrate.connect(create_default_groups, sender=self)


def create_default_groups(sender, **kwargs):
    """
    Create baseline groups and assign custom permissions.
    Idempotent: safe to run after every migration.
    """
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType
    from .models import Book

    content_type = ContentType.objects.get_for_model(Book)
    permissions = Permission.objects.filter(
        content_type=content_type,
        codename__in=['can_view', 'can_create', 'can_edit', 'can_delete'],
    )
    perms_by_code = {perm.codename: perm for perm in permissions}

    if len(perms_by_code) < 4:
        # Permissions not ready yet; let the next migration cycle create groups.
        return

    group_map = {
        'Viewers': ['can_view'],
        'Editors': ['can_view', 'can_create', 'can_edit'],
        'Admins': ['can_view', 'can_create', 'can_edit', 'can_delete'],
    }

    for group_name, perm_codes in group_map.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        for code in perm_codes:
            group.permissions.add(perms_by_code[code])
