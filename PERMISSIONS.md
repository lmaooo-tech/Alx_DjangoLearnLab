# Django Blog Permissions and Access Control Documentation

## Overview
This document provides comprehensive documentation for the permission and access control system in the Django Blog application. All views implement proper authentication and authorization checks using Django's built-in mixins and custom logic.

---

## Table of Contents
1. [Permission System Overview](#permission-system-overview)
2. [Django Built-in Mixins](#django-built-in-mixins)
3. [View-by-View Permissions](#view-by-view-permissions)
4. [Authentication Requirements](#authentication-requirements)
5. [Authorization Rules](#authorization-rules)
6. [Permission Error Handling](#permission-error-handling)
7. [Message Framework Integration](#message-framework-integration)
8. [URL Redirects](#url-redirects)
9. [Testing Permissions](#testing-permissions)
10. [Security Best Practices](#security-best-practices)

---

## Permission System Overview

### Three-Tier Permission Structure

```
1. Public Access (No Authentication)
   └─ PostListView (all users)
   └─ PostDetailView (all users)

2. Authentication Required
   └─ PostCreateView (logged-in users)
   └─ PostUpdateView (logged-in + author check)
   └─ PostDeleteView (logged-in + author check)

3. Author-Only Access
   └─ Edit own posts
   └─ Delete own posts
```

### Permission Flow Diagram

```
User Request
    ↓
Is Authenticated?
    ├─ NO → Redirect to Login
    │         ↓
    │    User logs in
    │         ↓
    │    Retry request
    │
    └─ YES → Is User Authorized?
             ├─ NO → 403 Forbidden (or redirect with message)
             │
             └─ YES → Process request
                      ↓
                   Return response
```

---

## Django Built-in Mixins

### LoginRequiredMixin
```python
from django.contrib.auth.mixins import LoginRequiredMixin

class MyView(LoginRequiredMixin, View):
    login_url = 'blog:login'  # URL to redirect if not authenticated
    redirect_field_name = 'next'  # Query parameter for post-login redirect
```

**Behavior**:
- Checks if user is authenticated
- If not: Redirects to `login_url` with `next` parameter
- If yes: Proceeds to view

**Configuration**:
```python
login_url = 'blog:login'  # URL name or path
redirect_field_name = 'next'  # Default is 'next'
```

**Example Redirect**:
```
User visits: /posts/new/  (not logged in)
Redirect to: /login/?next=/posts/new/
After login: /posts/new/ (original request)
```

### UserPassesTestMixin
```python
from django.contrib.auth.mixins import UserPassesTestMixin

class MyView(UserPassesTestMixin, View):
    def test_func(self):
        """Return True if user passes test, False otherwise"""
        return condition_check()
    
    def handle_no_permission(self):
        """Called if test_func returns False"""
        return redirect('some_url')
```

**Behavior**:
- Calls `test_func()` with current user/request
- If returns True: Proceeds to view
- If returns False: Calls `handle_no_permission()`
- Default `handle_no_permission()`: Returns 403 Forbidden

**Custom Error Handling**:
```python
def handle_no_permission(self):
    """Redirect with error message if permission denied"""
    messages.error(self.request, 'You do not have permission.')
    return redirect('some_view')
```

---

## View-by-View Permissions

### 1. PostListView

**Class Definition**:
```python
class PostListView(ListView):
    model = Post
    # No authentication required
```

**Access Control**:
- ✅ **Anonymous users**: Can view
- ✅ **Authenticated users**: Can view
- ✅ **Authors**: Can view and see edit/delete buttons on own posts

**URL**: `/posts/` or `/`  
**HTTP Method**: GET only  
**Template**: `blog/post_list.html`  

**Features**:
- Search functionality (query param: `?q=search`)
- Sort options (query param: `?sort_by=newest`)
- Pagination (query param: `?page=2`)
- Edit/Delete buttons visible only to post authors

**Example Access**:
```
Anonymous user:     /posts/  ✅ 200 OK
Authenticated user: /posts/  ✅ 200 OK
```

### 2. PostDetailView

**Class Definition**:
```python
class PostDetailView(DetailView):
    model = Post
    # No authentication required
```

**Access Control**:
- ✅ **Anonymous users**: Can view
- ✅ **Authenticated users**: Can view
- ✅ **Authors**: Can see edit/delete buttons

**URL**: `/posts/<int:pk>/`  
**HTTP Method**: GET only  
**Template**: `blog/post_detail.html`  

**Features**:
- Displays full post content
- Shows author information
- Shows edit/delete buttons only to author
- Provides `can_edit` context variable

**Context Variables**:
```python
{
    'post': Post object,
    'can_edit': Boolean (True if user is author)
}
```

**Example Access**:
```
GET /posts/1/
Anonymous user:     ✅ 200 OK
Authenticated user: ✅ 200 OK (can_edit=False unless author)
Non-existent post:  ❌ 404 Not Found
```

---

### 3. PostCreateView

**Class Definition**:
```python
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    login_url = 'blog:login'
```

**Access Control**:
- ❌ **Anonymous users**: Redirected to login
- ✅ **Authenticated users**: Can create

**URL**: `/posts/new/`  
**HTTP Methods**: 
- GET: Display form
- POST: Create post

**Template**: `blog/post_form.html`  

**Authentication Flow**:
```
Anonymous user visits /posts/new/
    ↓
LoginRequiredMixin checks is_authenticated
    ↓
False → Redirect to /login/?next=/posts/new/
         After login → Redirect to /posts/new/
         Then → Display form
```

**Form Processing**:
```python
def form_valid(self, form):
    form.instance.author = self.request.user  # Auto-set author
    response = super().form_valid(form)
    messages.success(self.request, 'Post created successfully!')
    return response
```

**Success Redirect**: `/posts/<new_post_id>/`  

**Messages**:
```
✅ "Post created successfully!"
```

**Example Access**:
```
Anonymous user:     /posts/new/ → 302 Redirect to /login/
Authenticated user: /posts/new/ → 200 OK, display form
```

**Important**: Author is set automatically to `request.user` - users cannot modify this in the form.

---

### 4. PostUpdateView

**Class Definition**:
```python
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    login_url = 'blog:login'
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
```

**Access Control**:
- ❌ **Anonymous users**: Redirected to login
- ❌ **Authenticated non-authors**: 403 Forbidden
- ✅ **Post author**: Can edit

**URL**: `/posts/<int:pk>/edit/`  
**HTTP Methods**: 
- GET: Display pre-filled form
- POST: Update post

**Template**: `blog/post_form.html`  

**Permission Check Flow**:
```
User visits /posts/1/edit/
    ↓
LoginRequiredMixin: Is authenticated?
    ├─ NO → Redirect to login
    │
    └─ YES → UserPassesTestMixin: Is author?
             ├─ NO → handle_no_permission() → Redirect with error
             │
             └─ YES → Display form
```

**Form Processing**:
```python
def form_valid(self, form):
    response = super().form_valid(form)
    messages.success(self.request, 'Post updated successfully!')
    return response
```

**Success Redirect**: `/posts/<id>/` (post detail)  

**Error Handling**:
```python
def handle_no_permission(self):
    messages.error(self.request, 'You do not have permission to edit this post.')
    return redirect('blog:post_detail', pk=self.object.pk)
```

**Messages**:
```
✅ "Post updated successfully!"
❌ "You don't have permission to edit this post."
```

**Example Access**:
```
Anonymous user:    /posts/1/edit/ → 302 Redirect to /login/?next=/posts/1/edit/
Other user:        /posts/1/edit/ → 302 Redirect to /posts/1/ with error message
Post author:       /posts/1/edit/ → 200 OK, display form
Non-existent post: /posts/99999/edit/ → 404 Not Found
```

---

### 5. PostDeleteView

**Class Definition**:
```python
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    login_url = 'blog:login'
    success_url = reverse_lazy('blog:post_list')
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
```

**Access Control**:
- ❌ **Anonymous users**: Redirected to login
- ❌ **Authenticated non-authors**: 403 Forbidden
- ✅ **Post author**: Can delete

**URL**: `/posts/<int:pk>/delete/`  
**HTTP Methods**: 
- GET: Display confirmation page
- POST: Delete post

**Template**: `blog/post_confirm_delete.html`  

**Confirmation Page Shows**:
- Post title
- Post excerpt (preview)
- Warning: "This action cannot be undone!"
- Buttons: "Yes, Delete" and "Cancel"

**Delete Processing**:
```python
def delete(self, request, *args, **kwargs):
    post_title = self.get_object().title
    response = super().delete(request, *args, **kwargs)
    messages.success(request, f'Post "{post_title}" deleted successfully!')
    return response
```

**Success Redirect**: `/posts/` (post list)  

**Error Handling**:
```python
def handle_no_permission(self):
    messages.error(self.request, 'You do not have permission to delete this post.')
    return redirect('blog:post_detail', pk=self.object.pk)
```

**Messages**:
```
✅ "Post 'Title' deleted successfully!"
❌ "You don't have permission to delete this post."
```

**Important Features**:
- Two-step process: Confirmation → Deletion
- POST-only deletion (prevents accidental deletion via GET)
- CSRF token required
- Permanent deletion (cannot be undone)

**Example Access**:
```
Anonymous user:    /posts/1/delete/ → 302 Redirect to /login/?next=/posts/1/delete/
Other user:        /posts/1/delete/ → 302 Redirect to /posts/1/ with error message
Post author (GET):  /posts/1/delete/ → 200 OK, display confirmation
Post author (POST): /posts/1/delete/ → 302 Redirect to /posts/, post deleted
```

---

## Authentication Requirements

### LoginRequiredMixin Behavior

**What Happens When User Is Not Authenticated**:
1. View checks `request.user.is_authenticated`
2. If False: Redirects to `login_url`
3. Includes `next` parameter with original URL
4. After login, user redirected back to original URL

**Configuration in Views**:
```python
class PostCreateView(LoginRequiredMixin, CreateView):
    login_url = 'blog:login'  # Where to redirect
    redirect_field_name = 'next'  # Query param name
```

**URL Redirect Pattern**:
```
Original request: /posts/new/
Not authenticated:
    Redirect to: /login/?next=/posts/new/
    
After login:
    Redirect to: /posts/new/  (from next param)
```

**In Templates - Check Authentication**:
```html
{% if user.is_authenticated %}
    <a href="{% url 'blog:post_create' %}">Create Post</a>
{% else %}
    <p><a href="{% url 'blog:login' %}">Login</a> to create a post</p>
{% endif %}
```

---

## Authorization Rules

### Object-Level Authorization (PostUpdateView and PostDeleteView)

**Check**: User == Post Author

```python
def test_func(self):
    """Only allow if user is the post author"""
    post = self.get_object()
    is_author = self.request.user == post.author
    return is_author
```

**Comparison**:
```python
self.request.user      # Current authenticated user object
post.author            # Post author user object

# Both are User model instances
# Comparison checks primary key equality
```

**Who Can Update/Delete**:
- ✅ Post author (person who created post)
- ❌ Other authenticated users
- ❌ Administrators (unless also author*)

*Note: Superusers bypass many checks, but we enforce author check in our test_func

---

## Permission Error Handling

### 404 Not Found
```
Situation: Post doesn't exist
URL: /posts/99999/
Response: 404 Not Found
```

**Automatic Django Behavior**:
- DetailView calls `get_object_or_404()`
- If post doesn't exist: Raises Http404
- Django renders 404 template

### 403 Forbidden
```
Situation: User not authorized (not author)
URL: /posts/1/edit/ (user is not author)
Response: 302 Redirect (we redirect instead of 403)
```

**Custom Handling**:
```python
def handle_no_permission(self):
    messages.error(self.request, 'Permission denied')
    return redirect('blog:post_detail', pk=self.object.pk)
```

**What We Do**:
- Show error message
- Redirect to post detail or list
- Not 403, but we notify user appropriately

### 302 Redirect (Login Required)
```
Situation: User not authenticated
URL: /posts/new/ (user not logged in)
Response: 302 Redirect to /login/?next=/posts/new/
```

**Django LoginRequiredMixin**:
```
POST ATTEMPT (authentication required)
    ↓
/posts/new/ (user not authenticated)
    ↓
102 Redirect to /login/?next=/posts/new/
    ↓
User logs in
    ↓
302 Redirect to /posts/new/
    ↓
Original request processed
```

---

## Message Framework Integration

### Success Messages
```python
# After post creation
messages.success(request, 'Post created successfully!')

# After post update
messages.success(request, 'Post updated successfully!')

# After post deletion
messages.success(request, 'Post "Title" deleted successfully!')
```

### Error Messages
```python
# Authorization failure
messages.error(request, 'You do not have permission to edit this post.')

# Type: error (displays in red/danger styling)
```

### Warning Messages
```python
# Permission check failure
messages.warning(request, 'You can only edit your own posts.')
```

**Display in Templates**:
```html
{% if messages %}
    {% for message in messages %}
        <div class="alert alert-{{ message.tags }}">
            {{ message }}
        </div>
    {% endfor %}
{% endif %}
```

**Message Storage**:
- Default: Session backend
- Persists through redirects
- Cleared after display

---

## URL Redirects

### Login Redirects
```
POST /posts/new/ (not authenticated)
    ↓
Response: 302 Redirect
Location: /login/?next=/posts/new/
```

**After Login**:
```
POST /login/ (credentials provided)
    ↓
Response: 302 Redirect
Location: /posts/new/  (from next parameter)
```

### Permission Denied Redirects
```
GET /posts/1/edit/ (authenticated, but not author)
    ↓
Response: 302 Redirect
Location: /posts/1/  (post detail)
With: Error message
```

### Success Redirects
```
POST /posts/new/ (create) → 302 → /posts/1/  (new post)
POST /posts/1/edit/ (update) → 302 → /posts/1/  (post detail)
POST /posts/1/delete/ (delete) → 302 → /posts/  (post list)
```

---

## Testing Permissions

### Test Scenarios

#### List View (Public Access)
```python
def test_post_list_accessible_to_anonymous_user(self):
    response = self.client.get('/posts/')
    self.assertEqual(response.status_code, 200)
```

#### Detail View (Public Access)
```python
def test_post_detail_accessible_to_anonymous_user(self):
    response = self.client.get('/posts/1/')
    self.assertEqual(response.status_code, 200)
```

#### Create View (Authenticated Only)
```python
def test_post_create_requires_authentication(self):
    response = self.client.get('/posts/new/')
    self.assertEqual(response.status_code, 302)  # Redirect to login

def test_post_create_accessible_to_authenticated_user(self):
    self.client.login(username='user', password='pass')
    response = self.client.get('/posts/new/')
    self.assertEqual(response.status_code, 200)
```

#### Edit View (Author Only)
```python
def test_post_edit_author_can_access(self):
    self.client.login(username='author', password='pass')
    response = self.client.get('/posts/1/edit/')
    self.assertEqual(response.status_code, 200)

def test_post_edit_non_author_denied(self):
    self.client.login(username='other', password='pass')
    response = self.client.get('/posts/1/edit/')
    self.assertIn(response.status_code, [302, 403])
```

#### Delete View (Author Only)
```python
def test_post_delete_author_can_access(self):
    self.client.login(username='author', password='pass')
    response = self.client.get('/posts/1/delete/')
    self.assertEqual(response.status_code, 200)

def test_post_delete_author_can_delete(self):
    self.client.login(username='author', password='pass')
    self.client.post('/posts/1/delete/')
    self.assertFalse(Post.objects.filter(pk=1).exists())
```

### Running Permission Tests
```bash
python manage.py test blog.tests.PermissionTests -v 2
python manage.py test blog.tests.PostCreatePermissionTests
python manage.py test blog.tests.PostEditPermissionTests
python manage.py test blog.tests.PostDeletePermissionTests
python manage.py test blog.tests.AccessControlMessageTests
```

---

## Security Best Practices

### 1. Always Use Mixins
✅ **Good**:
```python
class PostCreateView(LoginRequiredMixin, CreateView):
    pass
```

❌ **Bad**:
```python
class PostCreateView(CreateView):
    # No auth check!
    pass
```

### 2. Always Implement test_func
✅ **Good**:
```python
class PostUpdateView(UserPassesTestMixin, UpdateView):
    def test_func(self):
        return self.request.user == self.get_object().author
```

❌ **Bad**:
```python
class PostUpdateView(UpdateView):
    # No author check!
    pass
```

### 3. Never Trust User Input
✅ **Good**:
```python
# Author auto-set by view
form.instance.author = self.request.user
```

❌ **Bad**:
```html
<!-- Never let users set author -->
<input type="hidden" name="author" value="{{ request.POST.author }}">
```

### 4. Use POST for Modifications
✅ **Good**:
```python
# DeleteView accepts only POST
@require_http_methods(["GET", "POST"])
def post(self, request, *args, **kwargs):
    # Process deletion
```

❌ **Bad**:
```html
<!-- Never allow GET for deletion -->
<a href="/posts/1/delete/">Delete</a>  <!-- NO! -->
```

### 5. Use CSRF Protection
✅ **Good**:
```html
<form method="post">
    {% csrf_token %}
    <!-- Form fields -->
</form>
```

### 6. Display Appropriate Error Messages
✅ **Good**:
```python
messages.error(request, 'You do not have permission to edit this post.')
```

❌ **Bad**:
```python
# Generic message
messages.error(request, 'Error')
```

### 7. Validate in test_func
✅ **Good**:
```python
def test_func(self):
    try:
        post = self.get_object()
        return self.request.user == post.author
    except Post.DoesNotExist:
        return False
```

### 8. Log Permission Violations
```python
import logging
logger = logging.getLogger(__name__)

def handle_no_permission(self):
    logger.warning(f'Unauthorized access attempt by {self.request.user}')
    return redirect('blog:post_list')
```

---

## Common Permission Patterns

### Pattern 1: View Own Data
```python
class UserProfileView(LoginRequiredMixin, DetailView):
    def test_func(self):
        return self.request.user.pk == self.kwargs['pk']

def handle_no_permission(self):
    # Redirect to own profile
    return redirect('blog:profile', pk=self.request.user.pk)
```

### Pattern 2: Author-Only Modification
```python
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
```

### Pattern 3: Group-Based Access
```python
from django.contrib.auth.models import Group

class AdminOnlyView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Admins').exists():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
```

### Pattern 4: Staff Only
```python
class AdminView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
```

---

## Permission Summary Table

| View | Anonymous | Auth'd User | Author | Admin* |
|------|-----------|-------------|--------|--------|
| List | ✅ | ✅ | ✅ | ✅ |
| Detail | ✅ | ✅ | ✅ | ✅ |
| Create | ❌ | ✅ | ✅ | ✅ |
| Edit (own) | ❌ | ✅ | ✅ | ✅ |
| Edit (others) | ❌ | ❌ | ✅ | ✅ |
| Delete (own) | ❌ | ✅ | ✅ | ✅ |
| Delete (others) | ❌ | ❌ | ✅ | ✅ |

*Admins equal Authors if they created the post

---

## Troubleshooting

### Can't Access Create Page
- Are you logged in?
- Try: `/login/?next=/posts/new/`

### Can't Edit Post
- Are you the author?
- Try: Check post detail, edit button only visible to author
- Error message: "You do not have permission to edit this post."

### Can't Delete Post
- Are you the author?
- Try: Check post detail, delete button only visible to author
- Error message: "You do not have permission to delete this post."

### Strange Redirects
- Check `next` parameter
- Example: `/login/?next=/posts/1/` → after login → `/posts/1/`

---

*Last Updated: 2024*
*Django Version: 6.0.1*
*Python Version: 3.14+*
