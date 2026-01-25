# Permissions and Groups

This app uses custom permissions on the `Book` model:

- `can_view` – view book lists and details.
- `can_create` – add new books.
- `can_edit` – update existing books.
- `can_delete` – delete books.

## Default groups
A post-migrate hook creates/updates these groups automatically:
- Viewers: can_view
- Editors: can_view, can_create, can_edit
- Admins: can_view, can_create, can_edit, can_delete

You can manage or adjust these groups and permissions in the Django admin (Groups section). Re-running migrations will re-apply the baseline permissions to the groups.

## Views protected by permissions
- `list_all_books` and `LibraryDetailView`: require can_view
- `add_book`: requires can_create
- `edit_book`: requires can_edit
- `delete_book`: requires can_delete

## Quick testing flow
1. Run migrations so custom permissions exist, then start the server.
2. Create users in the admin and add them to Viewers, Editors, or Admins.
3. Log in as each user and verify access:
   - Viewers can only view lists/details.
   - Editors can view and add/edit but not delete.
   - Admins can perform all actions.
