# Django Blog Templates Documentation

## Overview
This document provides comprehensive documentation for all HTML templates used in the Django Blog application. All templates are built with Bootstrap styling, responsive design, and user-friendly interfaces.

---

## Table of Contents
1. [Template Hierarchy](#template-hierarchy)
2. [Base Template](#base-template)
3. [Authentication Templates](#authentication-templates)
4. [Blog Post Templates](#blog-post-templates)
5. [Template Tags & Filters](#template-tags--filters)
6. [Responsive Design](#responsive-design)
7. [Best Practices](#best-practices)
8. [Customization Guide](#customization-guide)

---

## Template Hierarchy

```
blog/
├── templates/
│   └── blog/
│       ├── base.html                      (Base layout)
│       ├── login.html                     (User authentication)
│       ├── register.html                  (User registration)
│       ├── profile.html                   (User profile)
│       ├── post_list.html                 (Blog post list + search/filter)
│       ├── post_detail.html               (Single post view)
│       ├── post_form.html                 (Create/edit post)
│       ├── post_confirm_delete.html       (Post deletion confirmation)
│       └── user_posts.html                (Author's posts)
```

All templates extend `base.html` which provides:
- Navigation header with login/logout links
- Responsive container structure
- Bootstrap styling
- Base CSS framework

---

## Base Template

**File**: [blog/templates/blog/base.html](blog/templates/blog/base.html)

### Purpose
Provides base layout and navigation for all pages in the application.

### Key Sections
```html
{% extends "django.contrib.admin:base_site.html" %}  (or custom base)
<header>
    <!-- Navigation with logo and links -->
    {% if user.is_authenticated %}
        <nav>
            - Dashboard
            - New Post (+ badge if available)
            - Profile
            - Logout
        </nav>
    {% else %}
        <nav>
            - Login
            - Register
        </nav>
    {% endif %}
</header>

{% block content %}
    <!-- Page-specific content -->
{% endblock %}

<footer>
    <!-- Site footer -->
</footer>
```

### Features
- **Responsive Navigation**: Adapts to mobile and desktop
- **Authentication State**: Shows different links based on login status
- **Dynamic Links**: Includes user profile and post creation links
- **Message Display**: Shows success/error messages from views
- **Static Assets**: Links to CSS and JavaScript files

### Usage Example
```html
{% extends 'blog/base.html' %}

{% block title %}Page Title{% endblock %}

{% block content %}
    <!-- Your page content here -->
{% endblock %}
```

---

## Authentication Templates

### login.html
**Purpose**: User login form

**Key Elements**:
- Username field (TextInput)
- Password field (PasswordInput)
- Remember me checkbox (optional)
- Submit button
- Registration link for new users
- Password reset link (future enhancement)

**Context Variables**:
- `form`: AuthenticationForm instance
- `next`: Redirect URL after login

**Example Access**: `/blog/login/`

### register.html
**Purpose**: User registration form

**Key Elements**:
- Username field with validation
- Email field with duplicate check
- Password field with requirements
- Password confirmation field
- First name field (optional)
- Last name field (optional)
- Submit button
- Login link for existing users

**Context Variables**:
- `form`: CustomUserCreationForm instance

**Example Access**: `/blog/register/`

**Validation Display**:
```html
{% if form.errors %}
    {% for field, errors in form.errors.items %}
        {{ field }}: {{ errors }}
    {% endfor %}
{% endif %}
```

### profile.html
**Purpose**: User profile view and edit

**Key Elements**:
- User avatar (profile picture or initials)
- Username and email
- Bio section (editable form)
- Location field (editable form)
- Website URL (editable form)
- Profile picture upload
- User statistics (post count)
- Edit profile button/form

**Context Variables**:
- `user`: User object
- `profile_form`: UserProfileForm instance
- `post_count`: Number of posts by user
- `can_edit`: Boolean for edit permissions

**Example Access**: `/blog/profile/`

---

## Blog Post Templates

### post_list.html
**Purpose**: Display all blog posts with search and filtering

**Key Features**:

#### 1. Header Section
```html
<h1>Blog Posts</h1>
{% if user.is_authenticated %}
    <a href="{% url 'post_create' %}">✎ Create New Post</a>
{% else %}
    <p><a href="{% url 'login' %}">Login</a> to create a post</p>
{% endif %}
```

#### 2. Search Section
```html
<form method="get" class="search-form">
    <input type="text" 
           name="q" 
           placeholder="Search by title, content, or author..."
           value="{{ search_query }}">
    <button type="submit">🔍 Search</button>
    {% if search_query %}
        <a href="{% url 'post_list' %}">Clear</a>
    {% endif %}
</form>
```

**Search Functionality**:
- Searches across post titles (case-insensitive)
- Searches across post content (case-insensitive)
- Searches across author usernames (case-insensitive)
- Results show count of matching posts
- Displays "No results found" message if needed

#### 3. Filter/Sort Section
```html
<form method="get" class="filter-form">
    <label for="sort_by">Sort by:</label>
    <select name="sort_by" id="sort_by">
        <option value="newest" selected>Newest First</option>
        <option value="oldest">Oldest First</option>
        <option value="title_asc">Title (A-Z)</option>
        <option value="title_desc">Title (Z-A)</option>
    </select>
</form>
```

**Sort Options**:
- `newest`: Most recently published posts first (default)
- `oldest`: Least recently published posts first
- `title_asc`: Posts sorted alphabetically by title (A-Z)
- `title_desc`: Posts sorted alphabetically by title (Z-A)

#### 4. Post Grid
```html
<div class="posts-grid">
    {% for post in posts %}
        <article class="post-card">
            <h2><a href="{% url 'post_detail' post.pk %}">{{ post.title }}</a></h2>
            
            <div class="post-meta">
                <span class="author">
                    By <a href="{% url 'user_posts' post.author.id %}">
                        {{ post.author.get_full_name|default:post.author.username }}
                    </a>
                </span>
                <time>{{ post.published_date|date:"M d, Y \a\t H:i" }}</time>
            </div>
            
            <div class="post-excerpt">
                <p>{{ post.content|truncatewords:30 }}</p>
            </div>
            
            <div class="post-footer">
                <a href="{% url 'post_detail' post.pk %}" class="read-more">Read More →</a>
                
                {% if user == post.author %}
                    <div class="post-actions">
                        <a href="{% url 'post_edit' post.pk %}" class="btn-small btn-edit">Edit</a>
                        <a href="{% url 'post_delete' post.pk %}" class="btn-small btn-delete">Delete</a>
                    </div>
                {% endif %}
            </div>
        </article>
    {% endfor %}
</div>
```

**Post Card Features**:
- Post title (clickable link)
- Author name with link to author's posts
- Publication date and time
- Post excerpt (30 words max with truncation)
- "Read More" link to full post
- Edit/Delete buttons (visible only to post author)
- Responsive grid layout (1-3 columns based on screen size)

#### 5. Pagination
```html
{% if is_paginated %}
    <div class="pagination">
        {% if page_obj.has_previous %}
            <a href="?page=1{% if search_query %}&q={{ search_query }}{% endif %}">« First</a>
            <a href="?page={{ page_obj.previous_page_number }}{% if search_query %}&q={{ search_query }}{% endif %}">‹ Previous</a>
        {% endif %}
        
        <span>Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}</span>
        
        {% if page_obj.has_next %}
            <a href="?page={{ page_obj.next_page_number }}{% if search_query %}&q={{ search_query }}{% endif %}">Next ›</a>
            <a href="?page={{ page_obj.paginator.num_pages }}{% if search_query %}&q={{ search_query }}{% endif %}">Last »</a>
        {% endif %}
    </div>
{% endif %}
```

**Pagination Features**:
- 10 posts per page (configurable)
- Previous/Next navigation
- First/Last page links
- Current page indicator
- Preserves search query and sort option across pages

**Context Variables**:
- `posts`: Paginated queryset of Post objects
- `is_paginated`: Boolean if results span multiple pages
- `page_obj`: Page object with pagination info
- `search_form`: PostSearchForm instance
- `filter_form`: PostFilterForm instance
- `search_query`: Current search term (if any)

**Example URLs**:
```
/blog/                              # All posts, newest first
/blog/?q=django                     # Search for 'django'
/blog/?sort_by=oldest               # Oldest posts first
/blog/?q=django&sort_by=title_asc   # Search + sort combined
/blog/?page=2                       # Second page of results
```

### post_detail.html
**Purpose**: Display full blog post with metadata and author info

**Key Sections**:

#### 1. Post Header
```html
<h1>{{ post.title }}</h1>

<div class="post-meta">
    <div class="author-info">
        <a href="{% url 'user_posts' post.author.id %}">
            {{ post.author.get_full_name|default:post.author.username }}
        </a>
        
        {% if post.author.profile.profile_picture %}
            <img src="{{ post.author.profile.profile_picture.url }}" 
                 alt="{{ post.author.username }}">
        {% else %}
            <div class="author-avatar-placeholder">
                {{ post.author.username|upper|slice:":1" }}
            </div>
        {% endif %}
    </div>
    
    <time>Published on {{ post.published_date|date:"F d, Y \a\t H:i" }}</time>
</div>
```

#### 2. Post Content
```html
<div class="post-content">
    {{ post.content|linebreaks }}
</div>
```

**Content Features**:
- Full post content displayed
- Line breaks preserved from database
- Text wrapping handles long URLs
- Responsive font sizing

#### 3. Post Actions (Author Only)
```html
{% if user == post.author %}
    <div class="post-actions">
        <a href="{% url 'post_edit' post.pk %}" class="btn btn-primary">
            ✎ Edit Post
        </a>
        <a href="{% url 'post_delete' post.pk %}" class="btn btn-danger">
            ✕ Delete Post
        </a>
    </div>
{% endif %}
```

#### 4. Navigation
```html
<div class="post-navigation">
    <a href="{% url 'post_list' %}" class="btn btn-secondary">← Back to Posts</a>
</div>
```

**Context Variables**:
- `post`: Post object with full details
- `can_edit`: Boolean indicating if user can edit (author only)

**Example Access**: `/blog/posts/1/`

### post_form.html
**Purpose**: Create or edit a blog post

**Key Features**:

#### 1. Form Header
```html
<div class="form-header">
    <h1>{{ action }} Blog Post</h1>
    <p class="form-subtitle">Share your thoughts with the community</p>
</div>
```

#### 2. Title Field
```html
<div class="form-group">
    <div class="label-wrapper">
        <label for="id_title">{{ form.title.label }}</label>
        <span class="required">*</span>
    </div>
    {{ form.title }}
    
    <div class="field-info">
        <span class="char-count">
            <span id="title_count">0</span>/200 characters
        </span>
        <small class="help-text">{{ form.title.help_text }}</small>
    </div>
    
    {% if form.title.errors %}
        <div class="form-errors">
            {% for error in form.title.errors %}
                <p class="error-icon">❌ {{ error }}</p>
            {% endfor %}
        </div>
    {% endif %}
</div>
```

**Title Validation**:
- Minimum 3 characters
- Maximum 200 characters
- Character counter updates in real-time
- Invalid characters blocked: `< > { }`

#### 3. Content Field
```html
<div class="form-group">
    <div class="label-wrapper">
        <label for="id_content">{{ form.content.label }}</label>
        <span class="required">*</span>
    </div>
    {{ form.content }}
    
    <div class="field-info">
        <span class="char-count">
            <span id="content_count">0</span> characters (minimum: 10)
        </span>
        <small class="help-text">{{ form.content.help_text }}</small>
    </div>
    
    {% if form.content.errors %}
        <div class="form-errors">
            {% for error in form.content.errors %}
                <p class="error-icon">❌ {{ error }}</p>
            {% endfor %}
        </div>
    {% endif %}
</div>
```

**Content Validation**:
- Minimum 10 characters
- Character counter updates in real-time
- Large textarea (10 rows)
- Preserves line breaks and formatting

#### 4. Form Actions
```html
<div class="form-actions">
    <button type="submit" class="btn btn-primary btn-lg">
        ✓ {{ action }} Post
    </button>
    <a href="{% url 'post_list' %}" class="btn btn-secondary btn-lg">
        ← Cancel
    </a>
</div>
```

#### 5. JavaScript Enhancement
```html
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Real-time character counters
    const titleInput = document.getElementById('id_title');
    const contentInput = document.getElementById('id_content');
    
    if (titleInput) {
        titleInput.addEventListener('input', function() {
            document.getElementById('title_count').textContent = this.value.length;
        });
    }
    
    if (contentInput) {
        contentInput.addEventListener('input', function() {
            document.getElementById('content_count').textContent = this.value.length;
        });
    }
    
    // Prevent double submission
    const form = document.querySelector('.post-form');
    form.addEventListener('submit', function(e) {
        const submitBtn = document.getElementById('submit-btn');
        submitBtn.disabled = true;
        submitBtn.textContent = '⏳ Submitting...';
    });
});
</script>
```

**Features**:
- Real-time character counters
- Form validation on submit
- Prevents double submission
- Shows loading state during submission
- Auto-focuses on first error field

**Context Variables**:
- `form`: PostForm instance
- `action`: "Create" or "Edit" (used in header and button)

**Example URLs**:
```
/blog/posts/create/           # Create new post
/blog/posts/1/edit/           # Edit post with ID 1
```

### post_confirm_delete.html
**Purpose**: Confirm deletion of a blog post

**Key Elements**:

#### 1. Warning Message
```html
<h1>Delete Post</h1>
<p class="warning">⚠️ Warning: This action cannot be undone!</p>
```

#### 2. Post Preview
```html
<div class="post-preview">
    <h3>{{ object.title }}</h3>
    <p class="preview-text">{{ object.content|truncatewords:30 }}</p>
</div>
```

#### 3. Confirmation Message
```html
<p class="confirmation-message">
    Are you sure you want to delete this post? 
    This action is permanent and cannot be reversed.
</p>
```

#### 4. Action Buttons
```html
<form method="post" class="delete-form">
    {% csrf_token %}
    <div class="form-actions">
        <button type="submit" class="btn btn-danger">Yes, Delete Post</button>
        <a href="{% url 'post_detail' object.pk %}" class="btn btn-secondary">Cancel</a>
    </div>
</form>
```

**Features**:
- Clear warning about permanent deletion
- Preview of post to be deleted
- Confirmation buttons
- Cancel option to return to post

**Context Variables**:
- `object`: Post object to be deleted

**Example Access**: `/blog/posts/1/delete/`

### user_posts.html
**Purpose**: Display all posts by a specific author

**Key Sections**:

#### 1. Author Header
```html
<div class="author-header">
    {% if author.profile.profile_picture %}
        <img src="{{ author.profile.profile_picture.url }}" 
             alt="{{ author.username }}">
    {% else %}
        <div class="author-avatar-placeholder">
            {{ author.username|upper|slice:":1" }}
        </div>
    {% endif %}
    
    <div class="author-details">
        <h1>{{ author.get_full_name|default:author.username }}</h1>
        <p class="username">@{{ author.username }}</p>
        
        {% if author.profile.bio %}
            <p class="bio">{{ author.profile.bio }}</p>
        {% endif %}
        
        {% if author.profile.location %}
            <p class="location">📍 {{ author.profile.location }}</p>
        {% endif %}
        
        <p class="member-since">
            Member since {{ author.date_joined|date:"F Y" }}
        </p>
    </div>
    
    <div class="author-stats">
        <div class="stat">
            <span class="stat-number">{{ post_count }}</span>
            <span class="stat-label">Post{{ post_count|pluralize }}</span>
        </div>
    </div>
</div>
```

**Author Information Displayed**:
- Profile picture or avatar placeholder
- Full name (or username if no full name)
- Username handle (@username)
- Bio/biography
- Location
- Member since date
- Post count statistics

#### 2. Posts Grid
```html
<h2>{{ author.username }}'s Posts</h2>
<div class="posts-grid">
    {% for post in posts %}
        <!-- Post card details (same as post_list.html) -->
    {% endfor %}
</div>
```

#### 3. No Posts Message
```html
{% if not posts %}
    <div class="no-posts">
        <p>{{ author.username }} hasn't posted yet.</p>
    </div>
{% endif %}
```

#### 4. Navigation
```html
<div class="back-link">
    <a href="{% url 'post_list' %}">← Back to All Posts</a>
</div>
```

**Context Variables**:
- `author`: User object whose posts are displayed
- `posts`: Queryset of posts by the author
- `post_count`: Number of posts by author

**Example Access**: `/blog/users/1/posts/`

---

## Template Tags & Filters

### Built-in Django Filters Used

#### 1. `|default`
```html
<!-- Use username if no full name -->
{{ post.author.get_full_name|default:post.author.username }}
```

#### 2. `|truncatewords`
```html
<!-- Truncate content to 30 words -->
{{ post.content|truncatewords:30 }}
```

#### 3. `|date`
```html
<!-- Format datetime to readable format -->
{{ post.published_date|date:"M d, Y \a\t H:i" }}
{{ user.date_joined|date:"F Y" }}
```

#### 4. `|upper` and `|slice`
```html
<!-- Convert to uppercase and get first character -->
{{ author.username|upper|slice:":1" }}
```

#### 5. `|linebreaks`
```html
<!-- Convert newlines to <p> and <br> tags -->
{{ post.content|linebreaks }}
```

#### 6. `|pluralize`
```html
<!-- Add 's' if count != 1 -->
{{ post_count|pluralize }}
```

### Custom Template Tags
Currently, no custom template tags are implemented. Future enhancements could include:
- `get_related_posts`: Get similar posts
- `format_content`: Apply markdown or syntax highlighting
- `user_avatar`: Generate user avatars

---

## Template Variables & Context

### Global Context (Available in all templates)
- `user`: Current authenticated user object
- `request`: HTTP request object
- `messages`: Message framework output
- `STATIC_URL`: Static files path

### View-Specific Context

#### PostListView
| Variable | Type | Description |
|----------|------|-------------|
| `posts` | QuerySet | Paginated posts (10 per page) |
| `is_paginated` | Boolean | Whether results span multiple pages |
| `page_obj` | Page | Pagination object |
| `search_form` | Form | PostSearchForm instance |
| `filter_form` | Form | PostFilterForm instance |
| `search_query` | String | Current search term |
| `title` | String | "All Blog Posts" |

#### PostDetailView
| Variable | Type | Description |
|----------|------|-------------|
| `post` | Post | Full post object |
| `can_edit` | Boolean | User can edit (author check) |

#### PostCreateView / PostUpdateView
| Variable | Type | Description |
|----------|------|-------------|
| `form` | Form | PostForm instance |
| `action` | String | "Create" or "Edit" |

#### PostDeleteView
| Variable | Type | Description |
|----------|------|-------------|
| `object` | Post | Post to be deleted |

#### UserPostsView
| Variable | Type | Description |
|----------|------|-------------|
| `author` | User | Author whose posts are shown |
| `posts` | QuerySet | Author's posts |
| `post_count` | Integer | Total posts by author |

---

## Responsive Design

### Breakpoints
```css
Desktop (>768px):
- Search/filter on same row
- Multi-column post grid (1-3 columns)
- Side-by-side form labels

Tablet (768px):
- Stacked search/filter
- 2-column post grid
- Adjusted padding

Mobile (<768px):
- Full-width search input
- Single-column post grid
- Stacked form fields
- Full-width buttons
```

### Mobile-Specific Features
- Touch-friendly button sizes (min 44px)
- Single-column layouts
- Readable font sizes (min 14px)
- Responsive images

---

## Best Practices

### 1. Template Security
✅ **Always use `{{ variable }}` for output** (escapes HTML)
❌ Don't use `|safe` unless absolutely necessary
✅ Use `{% csrf_token %}` on all forms
✅ Check user permissions with `{% if user.is_authenticated %}`

### 2. Accessibility
✅ Use semantic HTML (`<article>`, `<header>`, `<footer>`)
✅ Provide alt text for images
✅ Use proper heading hierarchy (h1, h2, h3)
✅ Link text should be descriptive

### 3. Performance
✅ Use `select_related()` and `prefetch_related()` in views
✅ Cache expensive queries
✅ Minimize template logic
✅ Use CDN for large images

### 4. Code Organization
✅ Keep templates DRY (Don't Repeat Yourself)
✅ Use template includes for repeated sections
✅ Use template inheritance (base.html)
✅ Keep template logic simple

### 5. Testing
✅ Test templates with different data sets
✅ Test responsive design on mobile devices
✅ Test with different browsers
✅ Validate HTML output

---

## Customization Guide

### Changing Colors
Edit CSS variables in `blog/static/css/styles.css`:
```css
/* Primary color (currently #4CAF50 green) */
.btn-primary, .read-more, a { color: #4CAF50; }

/* Danger color (currently #f44336 red) */
.btn-delete, .error { color: #f44336; }
```

### Modifying Post Grid Layout
```css
/* Change number of columns */
.posts-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    /* minmax(300px, 1fr) = minimum 300px columns */
}
```

### Adding New Form Fields
```python
# In blog/forms.py
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'content', 'new_field')  # Add here

# In blog/templates/blog/post_form.html
<div class="form-group">
    <label for="id_new_field">{{ form.new_field.label }}</label>
    {{ form.new_field }}
    {% if form.new_field.errors %}
        <div class="form-errors">
            {{ form.new_field.errors }}
        </div>
    {% endif %}
</div>
```

### Creating Template Includes
```html
<!-- blog/templates/blog/includes/post_card.html -->
<article class="post-card">
    <h2><a href="{% url 'post_detail' post.pk %}">{{ post.title }}</a></h2>
    <!-- Card content -->
</article>

<!-- Usage in post_list.html -->
{% include "blog/includes/post_card.html" %}
```

---

## Template Features Summary

| Feature | Location | Status |
|---------|----------|--------|
| Search posts | post_list.html | ✅ Active |
| Sort posts | post_list.html | ✅ Active |
| Pagination | post_list.html | ✅ Active (10/page) |
| Edit post | post_detail.html | ✅ Active (author only) |
| Delete post | post_confirm_delete.html | ✅ Active (author only) |
| Character counter | post_form.html | ✅ Active (JS) |
| Form validation | post_form.html | ✅ Active |
| Author profile | user_posts.html | ✅ Active |
| Responsive design | All templates | ✅ Active |

---

## Common Template Issues & Solutions

### Issue: CSS not loading
**Solution**: 
```bash
python manage.py collectstatic
# Then restart server
```

### Issue: Images not displaying
**Solution**:
- Check `MEDIA_URL` and `MEDIA_ROOT` in settings.py
- Ensure files exist in media directory
- Use `{{ object.image.url }}` not `{{ object.image }}`

### Issue: Pagination not preserving filters
**Solution**: Use query strings in pagination links:
```html
?page={{ page_obj.next_page_number }}&q={{ search_query }}&sort_by={{ sort_by }}
```

### Issue: Form not submitting
**Solution**:
- Ensure `{% csrf_token %}` present
- Check form method is `POST`
- Verify form.is_valid() in view

---

## Future Enhancements

Potential template improvements:
1. **Rich Text Editor**: TinyMCE or CKEditor for better content editing
2. **Markdown Preview**: Real-time markdown preview
3. **Drag & Drop Upload**: Image upload in posts
4. **Category/Tags**: Post categorization UI
5. **Comments**: Comment threads on posts
6. **Social Sharing**: Share buttons for social media
7. **Post Scheduling**: Schedule posts for future publishing
8. **Dark Mode**: Toggle dark/light theme
9. **Read Time**: Display estimated reading time
10. **Bookmarks**: Save favorite posts

---

## Performance Tips

### Template Rendering
- Limit queryset in loop: Use `paginate_by` in class-based views
- Use `select_related()` for ForeignKey: Reduces database queries
- Use `prefetch_related()` for ManyToMany: Optimizes related queries

### Caching
```python
# In views.py
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def post_list_view(request):
    pass
```

### Image Optimization
- Use appropriate image sizes
- Compress images before upload
- Use formats like WebP for modern browsers

---

*Last Updated: 2024*
*Django Version: 6.0.1*
*Python Version: 3.14+*
