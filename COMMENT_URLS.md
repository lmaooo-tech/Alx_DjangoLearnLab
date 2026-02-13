# Comment URL Patterns Documentation

## Overview
This document details all URL patterns for comment-related operations in the Django Blog application. All comment URLs follow RESTful conventions with intuitive path structures.

---

## URL Pattern Reference

### Comment Creation
```
Pattern: /posts/<int:post_pk>/comments/new/
Method: GET, POST
Name: blog:comment_create
View: CommentCreateView
Authentication: Required (LoginRequiredMixin)
```

**Description**: Route for authenticated users to create and post new comments on a blog post.

**URL Breakdown**:
- `/posts/` - Resource collection prefix
- `<int:post_pk>` - Primary key of the target post
- `/comments/` - Nested resource (comments belong to posts)
- `/new/` - Action suffix indicating creation

**Examples**:
```
GET  /posts/1/comments/new/     → Display comment form for post #1
POST /posts/1/comments/new/     → Submit new comment on post #1
POST /posts/42/comments/new/    → Submit new comment on post #42
```

**Rendered Form Variables**:
```python
{
    'post': <Post object>,
    'comment_form': <CommentForm instance>,
    'action': 'Post'
}
```

---

### Comment Update/Edit
```
Pattern: /comments/<int:comment_pk>/edit/
Method: GET, POST
Name: blog:comment_edit
View: CommentUpdateView
Authentication: Required (LoginRequiredMixin + UserPassesTestMixin)
```

**Description**: Route for authenticated comment authors to edit their own comments.

**URL Breakdown**:
- `/comments/` - Resource collection (direct reference, not nested)
- `<int:comment_pk>` - Primary key of the specific comment
- `/edit/` - Action suffix indicating modification

**Examples**:
```
GET  /comments/5/edit/    → Display edit form for comment #5
POST /comments/5/edit/    → Submit updates to comment #5
GET  /comments/123/edit/  → Display edit form for comment #123
```

**Permission Rules**:
- ✅ Comment author can edit
- ❌ Non-authors get 403 Forbidden + redirect
- ❌ Anonymous users redirected to login

**Rendered Form Variables**:
```python
{
    'post': <Post object>,
    'form': <CommentForm instance with existing content pre-filled>,
    'object': <Comment object>,
    'action': 'Edit'
}
```

---

### Comment Deletion
```
Pattern: /comments/<int:comment_pk>/delete/
Method: GET, POST
Name: blog:comment_delete
View: CommentDeleteView
Authentication: Required (LoginRequiredMixin + UserPassesTestMixin)
```

**Description**: Route for authenticated comment authors to delete their own comments with confirmation.

**URL Breakdown**:
- `/comments/` - Resource collection
- `<int:comment_pk>` - Primary key of the specific comment
- `/delete/` - Action suffix indicating removal

**Examples**:
```
GET  /comments/5/delete/     → Display deletion confirmation for comment #5
POST /comments/5/delete/     → Confirm deletion of comment #5
GET  /comments/123/delete/   → Display deletion confirmation for comment #123
```

**Two-Step Process**:
1. **GET Request**: Display confirmation page showing:
   - Comment preview (first 50 words)
   - Author name and timestamp
   - Post title (context)
   - Warning message
   - Cancel and Confirm buttons

2. **POST Request**: Process deletion
   - Require CSRF token (POST only)
   - Delete comment permanently
   - Redirect to post detail page
   - Display success message

**Permission Rules**:
- ✅ Comment author can delete
- ❌ Non-authors get 403 Forbidden + redirect
- ❌ Anonymous users redirected to login

**Rendered Template Variables**:
```python
{
    'object': <Comment object>,
    'post': <Post object>,
    'title': 'Delete Comment'
}
```

---

## Complete URL Configuration

```python
# In blog/urls.py
app_name = 'blog'

urlpatterns = [
    # ... other views ...
    
    # Comment CRUD URLs
    path('posts/<int:post_pk>/comments/new/', views.CommentCreateView.as_view(), name='comment_create'),
    path('comments/<int:comment_pk>/edit/', views.CommentUpdateView.as_view(), name='comment_edit'),
    path('comments/<int:comment_pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
]
```

---

## Template Tag Usage

### In Templates (comment_form.html)
```html
<!-- Creating a comment -->
<form method="post" action="{% url 'blog:comment_create' post.pk %}">
    {% csrf_token %}
    {{ form }}
    <button type="submit">Post Comment</button>
</form>

<!-- Editing a comment -->
<form method="post" action="{% url 'blog:comment_edit' comment.pk %}">
    {% csrf_token %}
    {{ form }}
    <button type="submit">Update Comment</button>
</form>

<!-- Deleting a comment -->
<form method="post" action="{% url 'blog:comment_delete' comment.pk %}">
    {% csrf_token %}
    <button type="submit">Delete Comment</button>
</form>
```

### In Templates (post_detail.html)
```html
<!-- Link to edit comment -->
<a href="{% url 'blog:comment_edit' comment.pk %}">Edit</a>

<!-- Link to delete comment -->
<a href="{% url 'blog:comment_delete' comment.pk %}">Delete</a>

<!-- Create comment form action -->
<form method="post" action="{% url 'blog:comment_create' post.pk %}">
    ...
</form>
```

---

## URL Parameters Reference

### post_pk (Post Primary Key)
- **Type**: Integer
- **Required for**: CommentCreateView
- **Used in**: Creating comments on a specific post
- **Example**: `1`, `42`, `999`

### comment_pk (Comment Primary Key)
- **Type**: Integer
- **Required for**: CommentUpdateView, CommentDeleteView
- **Used in**: Editing or deleting specific comments
- **Example**: `1`, `42`, `999`

---

## Request Flow Examples

### Create Comment Flow
```
User Action: Click "Post Comment" button
↓
GET /posts/1/comments/new/ 
↓
Django renders comment_form.html with CommentCreateView
↓
User fills form and submits
↓
POST /posts/1/comments/new/
↓
CommentCreateView.form_valid() executes:
  - Sets comment.author = request.user
  - Sets comment.post = Post(pk=1)
  - Saves comment to database
↓
302 Redirect to /posts/1/
↓
User sees success message
```

### Edit Comment Flow
```
User Action: Click "Edit" button on own comment
↓
GET /comments/5/edit/
↓
CommentUpdateView.test_func() checks: user == comment.author
↓
Django renders comment_form.html with pre-filled content
↓
User edits and submits
↓
POST /comments/5/edit/
↓
CommentUpdateView.form_valid() executes:
  - Updates comment.content
  - Sets comment.updated_at = now()
↓
302 Redirect to /posts/1/ (parent post)
↓
User sees success message
```

### Delete Comment Flow
```
User Action: Click "Delete" button on own comment
↓
GET /comments/5/delete/
↓
CommentDeleteView.test_func() checks: user == comment.author
↓
Django renders comment_confirm_delete.html with preview
↓
User clicks "Yes, Delete Comment"
↓
POST /comments/5/delete/
↓
CommentDeleteView.delete() executes:
  - Deletes comment from database
  - Permanent (cannot be undone)
↓
302 Redirect to /posts/1/ (parent post)
↓
User sees success message
↓
Comment no longer visible on post
```

---

## Permission & Authorization Matrix

| URL | GET | POST | Anonymous | Auth'd User | Comment Author | Non-Author | Superuser |
|-----|-----|------|-----------|-------------|----------------|------------|-----------|
| `/posts/<id>/comments/new/` | 🔐 | 🔐 | ❌ | ✅ | ✅ | ✅ | ✅ |
| `/comments/<id>/edit/` | 🔐 | 🔐 | ❌ | ❌ | ✅ | ❌ | ✅ |
| `/comments/<id>/delete/` | 🔐 | 🔐 | ❌ | ❌ | ✅ | ❌ | ✅ |

**Legend**:
- ✅ Allowed
- ❌ Denied/Redirected
- 🔐 Requires authentication (LoginRequiredMixin)

---

## Error Handling

### 404 Not Found
- Comment does not exist
- Post does not exist
- URL: `/comments/99999/edit/` (invalid comment ID)

### 403 Forbidden / Redirect
- User is not the comment author (non-authors)
- Redirects to post detail with error message
- Error: "You do not have permission to edit this comment."

### 302 Redirect to Login
- Anonymous user attempts to create/edit/delete comment
- Redirects to: `/login/?next=/posts/1/comments/new/`
- After login, user returned to original URL via `next` parameter

### 400 Bad Request / Form Validation
- Comment content < 3 characters
- Comment content > 5000 characters
- Form displays with error messages

---

## Best Practices & Tips

### 1. Always Use URL Names
```html
<!-- ✅ GOOD -->
<a href="{% url 'blog:comment_edit' comment.pk %}">Edit</a>

<!-- ❌ BAD -->
<a href="/comments/5/edit/">Edit</a>
```

### 2. Always Include CSRF Token
```html
<!-- ✅ GOOD -->
<form method="post">
    {% csrf_token %}
    {{ form }}
</form>

<!-- ❌ BAD -->
<form method="post">
    {{ form }}
</form>
```

### 3. Redirect with Next Parameter
```html
<!-- ✅ GOOD - Returns to post after login -->
<a href="{% url 'blog:login' %}?next={% url 'post_detail' post.pk %}">Login</a>

<!-- ❌ BAD - Returns to home after login -->
<a href="{% url 'blog:login' %}">Login</a>
```

### 4. Use Reverse in Views
```python
# ✅ GOOD
return redirect('blog:post_detail', pk=post.pk)

# ❌ BAD
return redirect(f'/posts/{post.pk}/')
```

### 5. Handle Inaccessible Comments
```python
# ✅ GOOD
def test_func(self):
    try:
        comment = self.get_object()
        return self.request.user == comment.author
    except Comment.DoesNotExist:
        return False

# ❌ BAD
def test_func(self):
    return self.request.user == self.get_object().author
```

---

## URL Namespace Usage

All URLs are namespaced with `app_name = 'blog'`, so always include the namespace prefix:

```django
{# ✅ CORRECT - With namespace #}
{% url 'blog:comment_create' post.pk %}
{% url 'blog:comment_edit' comment.pk %}
{% url 'blog:comment_delete' comment.pk %}

{# ❌ INCORRECT - Without namespace #}
{% url 'comment_create' post.pk %}
{% url 'comment_edit' comment.pk %}
{% url 'comment_delete' comment.pk %}
```

---

## URL Routing Decision Architecture

```
Request → Django Router
           ↓
    [Incoming URL]
           ↓
    /posts/1/comments/new/        → CommentCreateView (POST form)
    /posts/1/comments/new/ (POST) → CommentCreateView.form_valid() → Save → Redirect
    /comments/5/edit/             → CommentUpdateView (Edit form)
    /comments/5/edit/ (POST)      → CommentUpdateView.form_valid() → Update → Redirect
    /comments/5/delete/           → CommentDeleteView (Confirm)
    /comments/5/delete/ (POST)    → CommentDeleteView.delete() → Remove → Redirect
```

---

## Related Resources

- [Views Documentation](COMMENT_VIEWS.md)
- [Forms Documentation](COMMENT_FORMS.md)
- [Models Documentation](blog/models.py)
- [Templates Documentation](COMMENT_TEMPLATES.md)
- [Permissions Documentation](PERMISSIONS.md)

---

*Last Updated: February 2026*
*Django Version: 6.0.1*
