# Django Blog URL Configuration Guide

## Overview
This document provides complete documentation for URL routing in the Django Blog application. All URLs follow RESTful principles with intuitive, descriptive patterns for easy navigation and maintenance.

---

## Table of Contents
1. [URL Structure](#url-structure)
2. [Authentication URLs](#authentication-urls)
3. [Blog Post CRUD URLs](#blog-post-crud-urls)
4. [Author/User URLs](#authoruser-urls)
5. [URL Naming Convention](#url-naming-convention)
6. [URL Parameters](#url-parameters)
7. [Reverse URL Lookup](#reverse-url-lookup)
8. [URL Testing](#url-testing)
9. [Best Practices](#best-practices)

---

## URL Structure

### Base Application Namespace
```python
app_name = 'blog'
```

All URLs are under the `blog` namespace, allowing for:
- Organized URL management
- Conflict prevention with other apps
- Template usage: `{% url 'blog:post_list' %}`
- View usage: `reverse('blog:post_list')`

### URL Categories
```
/                           → Authentication & Home
/register/                  → User Registration
/login/                     → User Login
/logout/                    → User Logout
/profile/                   → User Profile

/posts/                     → Blog Post Listing (with search/filter)
/posts/new/                 → Create New Post
/posts/<int:pk>/            → View Post Details
/posts/<int:pk>/edit/       → Edit Post
/posts/<int:pk>/delete/     → Delete Post Confirmation

/users/<int:pk>/posts/      → View All Posts by User
```

---

## Authentication URLs

### 1. User Registration
**URL**: `/register/`  
**Name**: `blog:register`  
**Method**: GET, POST  
**View**: `blog.views.register` (Function-based)  
**Authentication**: Not required (redirects if already logged in)  
**Template**: `blog/register.html`  
**Form**: `CustomUserCreationForm`  

**Purpose**: Allow new users to create accounts

**Access**:
- GET: Display registration form
- POST: Process form submission and create user

**Redirect on Success**: 
- Logs user in and redirects to `/profile/`

**Usage in Templates**:
```html
<a href="{% url 'blog:register' %}">Create Account</a>
```

**Usage in Views**:
```python
from django.urls import reverse
redirect(reverse('blog:register'))
```

---

### 2. User Login
**URL**: `/login/`  
**Name**: `blog:login`  
**Method**: GET, POST  
**View**: `blog.views.login_view` (Function-based)  
**Authentication**: Not required (redirects if already logged in)  
**Template**: `blog/login.html`  
**Form**: Django's `AuthenticationForm`  

**Purpose**: Authenticate existing users

**Access**:
- GET: Display login form
- POST: Process credentials and establish session

**Query Parameters**:
- `next`: Redirect URL after successful login
  - Example: `/login/?next=/posts/1/`
  - Redirects to `/posts/1/` after login

**Redirect on Success**:
- Redirects to `next` parameter if provided
- Otherwise redirects to `/profile/`

**Usage in Templates**:
```html
<a href="{% url 'blog:login' %}">Login</a>

<!-- With next parameter -->
<a href="{% url 'blog:login' %}?next={% url 'blog:posts' %}">Login to Create Post</a>
```

---

### 3. User Logout
**URL**: `/logout/`  
**Name**: `blog:logout`  
**Method**: POST  
**View**: `blog.views.logout_view` (Function-based)  
**Authentication**: Required (LoginRequiredMixin)  
**Template**: None (redirects immediately)  

**Purpose**: Terminate user session and log out

**Security**:
- POST-only endpoint (prevents accidental logout via GET)
- CSRF token required
- Session destroyed
- User redirected to login page

**Usage in Templates**:
```html
<form method="post" action="{% url 'blog:logout' %}">
    {% csrf_token %}
    <button type="submit">Logout</button>
</form>
```

---

### 4. User Profile
**URL**: `/profile/`  
**Name**: `blog:profile`  
**Method**: GET, POST  
**View**: `blog.views.profile` (Function-based)  
**Authentication**: Required (LoginRequiredMixin)  
**Template**: `blog/profile.html`  
**Forms**: 
- `UserProfileForm` (for profile editing)
- Profile display from UserProfile model

**Purpose**: View and edit user profile information

**Access**:
- GET: Display user profile and edit form
- POST: Update profile information (bio, location, website, picture)

**User-Specific**: Each user can only view/edit their own profile

**Accessible To**:
- Authenticated users only
- Each user sees their own profile

**Usage in Templates**:
```html
<a href="{% url 'blog:profile' %}">My Profile</a>
```

---

## Blog Post CRUD URLs

### 5. Post List (All Posts)
**URL**: `/` or `/posts/`  
**Names**: `blog:post_list`, `blog:posts`  
**Method**: GET  
**View**: `blog.views.PostListView` (Class-based ListView)  
**Authentication**: Not required  
**Template**: `blog/post_list.html`  

**Purpose**: Display all blog posts with search and filtering

**Query Parameters**:
- `q`: Search query (searches title, content, author)
  - Example: `/posts/?q=django`
- `sort_by`: Sort order (newest, oldest, title_asc, title_desc)
  - Example: `/posts/?sort_by=oldest`
- `page`: Page number for pagination
  - Example: `/posts/?page=2`

**Combination Examples**:
```
/posts/                                    # All posts, newest first
/posts/?q=tutorial                         # Search for 'tutorial'
/posts/?sort_by=title_asc                  # Sort by title A-Z
/posts/?q=python&sort_by=newest            # Search + sort
/posts/?q=django&page=2                    # Search + pagination
/posts/?q=blog&sort_by=oldest&page=1       # All parameters
```

**Context Data**:
- `posts`: Paginated queryset (10 per page)
- `is_paginated`: Boolean
- `page_obj`: Pagination object
- `search_form`: PostSearchForm
- `filter_form`: PostFilterForm
- `search_query`: Current search term

**Features**:
- ✅ Full-text search (title, content, author)
- ✅ Multiple sort options
- ✅ Pagination (10 posts per page)
- ✅ Responsive grid layout

**Usage in Templates**:
```html
<a href="{% url 'blog:posts' %}">All Posts</a>
<a href="{% url 'blog:posts' %}?sort_by=oldest">Oldest Posts</a>
```

---

### 6. Create New Post
**URL**: `/posts/new/`  
**Name**: `blog:post_create`  
**Method**: GET, POST  
**View**: `blog.views.PostCreateView` (Class-based CreateView)  
**Authentication**: Required (LoginRequiredMixin)  
**Template**: `blog/post_form.html`  
**Form**: `PostForm`  

**Purpose**: Create a new blog post

**Access**:
- GET: Display blank post creation form
- POST: Process form and create post

**Form Fields**:
- `title`: Post title (required, 3-200 chars)
- `content`: Post content (required, 10+ chars)

**Author Assignment**: 
- Automatically set to current user
- Cannot be modified in form (security measure)

**Validation**:
- Title: 3-200 characters, no special chars
- Content: 10+ characters
- Content must differ from title

**Redirect on Success**: 
- Redirects to `/posts/<id>/` (post detail view)
- Shows success message

**Usage in Templates**:
```html
<!-- Button visible only to authenticated users -->
{% if user.is_authenticated %}
    <a href="{% url 'blog:post_create' %}" class="btn btn-primary">
        Create New Post
    </a>
{% endif %}
```

**Unauthenticated Access**:
- Redirects to `/login/?next=/posts/new/`
- After login, redirects back to `/posts/new/`

---

### 7. View Post Details
**URL**: `/posts/<int:pk>/`  
**Name**: `blog:post_detail`  
**Method**: GET  
**View**: `blog.views.PostDetailView` (Class-based DetailView)  
**Authentication**: Not required  
**Template**: `blog/post_detail.html`  
**Primary Key**: Post ID (auto-incremented integer)

**Purpose**: Display full post with all details

**URL Examples**:
```
/posts/1/          # View post with ID 1
/posts/42/         # View post with ID 42
/posts/999/        # View post with ID 999
```

**Context Data**:
- `post`: Full Post object with all fields
- `can_edit`: Boolean (True if user is author)

**Post Information Displayed**:
- Full title
- Complete content with formatting
- Author name and profile picture
- Publication date and time
- Edit/Delete buttons (author only)

**Error Handling**:
- Returns 404 if post ID doesn't exist
- Example: `/posts/99999/` → 404 Not Found

**Usage in Templates**:
```html
<!-- From post list -->
<a href="{% url 'blog:post_detail' post.pk %}">Read More</a>

<!-- In post card -->
<a href="{% url 'blog:post_detail' post.id %}">{{ post.title }}</a>
```

**Usage in Views**:
```python
post_url = reverse('blog:post_detail', kwargs={'pk': post.id})
redirect(post_url)
```

---

### 8. Edit Post
**URL**: `/posts/<int:pk>/edit/`  
**Name**: `blog:post_edit`  
**Method**: GET, POST  
**View**: `blog.views.PostUpdateView` (Class-based UpdateView)  
**Authentication**: Required (LoginRequiredMixin)  
**Authorization**: User must be post author (UserPassesTestMixin)  
**Template**: `blog/post_form.html`  
**Form**: `PostForm`  
**Primary Key**: Post ID to be edited

**Purpose**: Edit an existing blog post

**URL Examples**:
```
/posts/1/edit/     # Edit post with ID 1
/posts/42/edit/    # Edit post with ID 42
```

**Access Control**:
- Only the post author can edit
- Other users get 403 Forbidden

**Access**:
- GET: Display form pre-filled with post data
- POST: Process form and update post

**Form Behavior**:
- Pre-populated with current title and content
- Same validation rules as create
- Author cannot be changed

**Redirect on Success**: 
- Redirects to `/posts/<id>/` (post detail)
- Shows success message

**Forbidden Access**:
- Non-author attempts → 403 Forbidden
- Example response: "You don't have permission to edit this post"

**Unauthenticated Access**:
- Redirects to `/login/?next=/posts/1/edit/`
- After login, attempts to redirect back (if user is author)

**Usage in Templates**:
```html
<!-- Only shown to post author -->
{% if user == post.author %}
    <a href="{% url 'blog:post_edit' post.pk %}">Edit Post</a>
{% endif %}
```

---

### 9. Delete Post
**URL**: `/posts/<int:pk>/delete/`  
**Name**: `blog:post_delete`  
**Method**: GET, POST  
**View**: `blog.views.PostDeleteView` (Class-based DeleteView)  
**Authentication**: Required (LoginRequiredMixin)  
**Authorization**: User must be post author (UserPassesTestMixin)  
**Template**: `blog/post_confirm_delete.html`  
**Primary Key**: Post ID to be deleted

**Purpose**: Delete a blog post with confirmation

**URL Examples**:
```
/posts/1/delete/   # Delete post with ID 1
/posts/42/delete/  # Delete post with ID 42
```

**Access Control**:
- Only the post author can delete
- Other users get 403 Forbidden

**Access**:
- GET: Display confirmation page
- POST: Process deletion and remove post

**Confirmation Page Shows**:
- Post title
- Post preview (30-word excerpt)
- Warning: "This action cannot be undone"
- Confirm/Cancel buttons

**Redirect on Success**: 
- Redirects to `/posts/` (post list)
- Confirmation message shown

**Forbidden Access**:
- Non-author attempts → 403 Forbidden

**Unauthenticated Access**:
- Redirects to `/login/?next=/posts/1/delete/`

**Permanent Deletion**:
- Post is immediately deleted from database
- Cannot be recovered
- All post comments removed (if such feature added)

**Usage in Templates**:
```html
<!-- Only shown to post author -->
{% if user == post.author %}
    <a href="{% url 'blog:post_delete' post.pk %}" class="btn btn-danger">
        Delete Post
    </a>
{% endif %}
```

---

## Author/User URLs

### 10. User Posts
**URL**: `/users/<int:pk>/posts/`  
**Name**: `blog:user_posts`  
**Method**: GET  
**View**: `blog.views.UserPostsView` (Class-based ListView)  
**Authentication**: Not required  
**Template**: `blog/user_posts.html`  
**Primary Key**: User ID

**Purpose**: Display all posts by a specific author

**URL Examples**:
```
/users/1/posts/    # All posts by user with ID 1
/users/42/posts/   # All posts by user with ID 42
```

**Context Data**:
- `author`: User object whose posts are displayed
- `posts`: Queryset of posts by author
- `post_count`: Number of posts by author

**Author Information Displayed**:
- Profile picture
- Username and full name
- Bio (if provided)
- Location (if provided)
- Member since date
- Post count

**Features**:
- ✅ Author profile header
- ✅ All author's posts in grid
- ✅ Edit/Delete buttons (if viewing own profile)
- ✅ Link to author's other posts

**Error Handling**:
- Returns 404 if user ID doesn't exist

**Usage in Templates**:
```html
<!-- Link to author profile -->
<a href="{% url 'blog:user_posts' post.author.pk %}">
    {{ post.author.username }}'s Posts
</a>

<!-- From post cards -->
<a href="{% url 'blog:user_posts' author.id %}">
    View all from {{ author.username }}
</a>
```

---

## URL Naming Convention

### Naming Scheme
All URL names follow the pattern: `blog:<resource>_<action>`

| Resource | List | Detail | Create | Update | Delete |
|----------|------|--------|--------|--------|--------|
| post | post_list | post_detail | post_create | post_edit | post_delete |
| user | - | - | - | - | - |
| auth | - | - | register | - | logout |

### Naming Examples
- `blog:posts` - List all posts
- `blog:post_detail` - View single post
- `blog:post_create` - Create new post
- `blog:post_edit` - Edit post
- `blog:post_delete` - Delete post
- `blog:user_posts` - View user's posts
- `blog:register` - User registration
- `blog:login` - User login
- `blog:logout` - User logout
- `blog:profile` - User profile

---

## URL Parameters

### Primary Key (pk)
- **Type**: Integer
- **Description**: Unique identifier for Post or User objects
- **Example**: `/posts/1/` (Post with ID 1)
- **Auto-increment**: IDs automatically assigned on creation

### Query String Parameters

#### Search (q)
```
GET /posts/?q=django
```
- **Parameter Name**: `q`
- **Type**: String (2-200 characters)
- **Function**: Searches post title, content, and author username
- **Case-sensitive**: No (icontains lookup)

#### Sorting (sort_by)
```
GET /posts/?sort_by=newest
```
- **Parameter Name**: `sort_by`
- **Valid Values**: 
  - `newest` (default)
  - `oldest`
  - `title_asc`
  - `title_desc`
- **Default**: `newest`

#### Pagination (page)
```
GET /posts/?page=2
```
- **Parameter Name**: `page`
- **Type**: Integer
- **Default**: 1
- **Items per page**: 10

#### Next (next)
```
GET /login/?next=/posts/1/
```
- **Parameter Name**: `next`
- **Function**: Redirect URL after successful action
- **Common Uses**:
  - Post-login redirect: `/login/?next=/posts/new/`
  - Post-logout redirect: Configurable in views

### Combining Parameters
```
/posts/?q=tutorial&sort_by=oldest&page=1
/posts/?q=python&sort_by=title_asc
/login/?next=/posts/42/edit/
```

---

## Reverse URL Lookup

### In Templates
```html
<!-- Using url tag -->
<a href="{% url 'blog:post_detail' post.pk %}">View Post</a>
<a href="{% url 'blog:posts' %}?page=2">Next Page</a>

<!-- With query params -->
<a href="{% url 'blog:posts' %}?q=django&sort_by=newest">Search Results</a>
```

### In Views
```python
from django.urls import reverse
from django.shortcuts import redirect

# Simple URL
url = reverse('blog:post_list')  # Returns '/posts/'

# With parameters
url = reverse('blog:post_detail', kwargs={'pk': 1})  # Returns '/posts/1/'

# Redirect usage
redirect(reverse('blog:post_list'))

# Redirect with query params
from django.http import QueryDict
redirect(reverse('blog:posts') + '?page=2')
```

### In Forms and AJAX
```python
# Get URL in form action
form_url = reverse('blog:post_create')
# Result: /posts/new/

# Dynamic form submission
post_url = reverse('blog:post_detail', args=[post_id])
```

---

## URL Testing

### Testing URL Resolution
```bash
# Django shell
python manage.py shell

# Test URL reversing
from django.urls import reverse
reverse('blog:post_list')  # '/posts/'
reverse('blog:post_detail', kwargs={'pk': 1})  # '/posts/1/'

# Test URL reversal
from django.urls import resolve
resolve('/posts/').view_name  # 'blog:post_list'
resolve('/posts/1/').view_name  # 'blog:post_detail'
```

### Manual Testing Checklist
- [ ] `/` loads post list
- [ ] `/posts/` loads post list
- [ ] `/posts/new/` requires login (redirects to login)
- [ ] `/posts/1/` shows post details
- [ ] `/posts/1/edit/` requires being post author
- [ ] `/posts/1/delete/` requires being post author
- [ ] `/users/1/posts/` shows user's posts
- [ ] `/register/` loads registration form
- [ ] `/login/` loads login form
- [ ] `/logout/` logs out user
- [ ] `/profile/` shows user profile
- [ ] Query params work: `/posts/?q=test&sort_by=oldest`
- [ ] 404 on non-existent post: `/posts/99999/`
- [ ] 403 on unauthorized access

### Test Using Django's Test Client
```python
from django.test import Client

client = Client()

# Test GET requests
response = client.get('/posts/')
assert response.status_code == 200

# Test with authentication
from django.contrib.auth.models import User
user = User.objects.create_user('test', 'test@example.com', 'pass')
client.login(username='test', password='pass')
response = client.get('/posts/new/')
assert response.status_code == 200

# Test with query params
response = client.get('/posts/?q=django&sort_by=newest')
assert response.status_code == 200
```

---

## Best Practices

### 1. Always Use URL Names (Never Hard-code URLs)
✅ **Good**:
```html
<a href="{% url 'blog:post_list' %}">Posts</a>
```

❌ **Bad**:
```html
<a href="/posts/">Posts</a>
```

**Why**: If URL patterns change, hard-coded URLs break

### 2. Use Namespace in Templates
✅ **Good**:
```html
<a href="{% url 'blog:post_detail' post.pk %}">View</a>
```

❌ **Bad** (if used):
```html
<a href="{% url 'post_detail' post.pk %}">View</a>
```

**Why**: Prevents conflicts with other apps' URL names

### 3. Include Query Parameters in Links
✅ **Good**:
```html
<a href="{% url 'blog:posts' %}?sort_by=oldest">Oldest First</a>
```

### 4. Use Appropriate HTTP Methods
- GET: Display pages, retrieve data
- POST: Form submissions, create/update/delete
- Never use GET for actions with side effects

### 5. Use Authentication Mixins
✅ **Good**:
```python
class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = 'blog/post_form.html'
    # ...
```

**Why**: Automatic permission handling

### 6. Proper Error Handling
- Return 404 for missing resources
- Return 403 for unauthorized access
- Provide helpful error messages

### 7. Use Semantic URL Structure
```
/posts/            # Plural (resource collection)
/posts/<int:pk>/   # With ID (specific resource)
/posts/new/        # Action (create)
/posts/<int:pk>/edit/  # Hierarchical (resource action)
```

### 8. RESTful API Consistency
```
GET    /posts/             # List
POST   /posts/             # Create
GET    /posts/<id>/        # Detail
PUT    /posts/<id>/        # Full update
PATCH  /posts/<id>/        # Partial update
DELETE /posts/<id>/        # Delete
```

### 9. Performance Considerations
- Use query parameters for filtering (not URL path)
- Example: `/posts/?q=search` (not `/posts/search/`)
- Helps with caching and URL patterns

### 10. Security Best Practices
- Never expose sensitive IDs in URLs
- Use slugs for public URLs when possible
- Validate all URL parameters in views
- Use UserPassesTestMixin for authorization

---

## URL Troubleshooting

### Issue: URLs not working
**Solution**:
1. Check URL spelling in templates: `{% url 'blog:post_list' %}`
2. Verify URL name matches urls.py: `name='post_list'`
3. Check app namespace: `app_name = 'blog'`
4. Restart Django development server

### Issue: 404 errors on valid URLs
**Solution**:
- Check URL pattern matches: `/posts/<int:pk>/` matches `/posts/1/`
- Verify pk is integer, not string
- Check database for resource: Post with ID 1 exists?

### Issue: 403 Forbidden on permitted URLs
**Solution**:
- Check UserPassesTestMixin logic
- Verify user.is_authenticated
- Check post.author == request.user for edit/delete

### Issue: Query parameters not working
**Solution**:
- Query params handled in view, not URL pattern
- Access in view: `request.GET.get('q')`
- Template: `{{ request.GET.q }}` or `{{ search_query }}`

---

## URL Reference Table

| Endpoint | HTTP | Auth? | View | Name | Purpose |
|----------|------|-------|------|------|---------|
| `/register/` | GET/POST | No | register | register | Sign up |
| `/login/` | GET/POST | No | login_view | login | Sign in |
| `/logout/` | POST | Yes | logout_view | logout | Sign out |
| `/profile/` | GET/POST | Yes | profile | profile | User profile |
| `/` | GET | No | PostListView | post_list | List posts |
| `/posts/` | GET | No | PostListView | posts | List posts |
| `/posts/new/` | GET/POST | Yes | PostCreateView | post_create | Create post |
| `/posts/<id>/` | GET | No | PostDetailView | post_detail | View post |
| `/posts/<id>/edit/` | GET/POST | Yes* | PostUpdateView | post_edit | Edit post |
| `/posts/<id>/delete/` | GET/POST | Yes* | PostDeleteView | post_delete | Delete post |
| `/users/<id>/posts/` | GET | No | UserPostsView | user_posts | User posts |

*Author only

---

## Future URL Enhancements

Potential URLs for future features:
- `/api/posts/` - REST API endpoints
- `/posts/<slug>/` - Slug-based URLs
- `/posts/search/` - Advanced search
- `/posts/<int:pk>/comments/` - Post comments
- `/posts/<int:pk>/like/` - Like functionality
- `/category/<slug>/` - Posts by category
- `/tags/<slug>/` - Posts by tag
- `/users/<username>/` - User profile by username

---

## Configuration in settings.py

### Include URLs in Main Project
**File**: `django_blog/urls.py`

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### URL Prefix
- All blog URLs are under `/blog/` prefix
- Full URL: `/blog/posts/`
- Optional: Can be changed to `path('', include('blog.urls'))` for root-level access

---

*Last Updated: 2024*
*Django Version: 6.0.1*
*Python Version: 3.14+*
