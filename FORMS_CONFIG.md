# Django Blog Forms Configuration Guide

## Overview
This document provides comprehensive documentation for all forms used in the Django Blog application. All forms include proper validation, Bootstrap styling, and security measures.

---

## Table of Contents
1. [CustomUserCreationForm](#customusercreationform)
2. [UserProfileForm](#userprofileform)
3. [PostForm](#postform)
4. [PostSearchForm](#postsearchform)
5. [PostFilterForm](#postfilterform)
6. [Form Security](#form-security)
7. [Validation Strategies](#validation-strategies)
8. [Form Testing](#form-testing)

---

## CustomUserCreationForm

### Purpose
Used for user registration with email validation and password security.

### Fields
- **username**: CharField (required)
  - Validation: Django default (alphanumeric, underscore, hyphen)
  - Widget: TextInput with Bootstrap styling
  - Help Text: Explains username requirements

- **email**: EmailField (required)
  - Validation: Email format + uniqueness
  - Widget: EmailInput with Bootstrap styling
  - Error Message: "Email already registered" if duplicate

- **password1**: CharField (required)
  - Validation: Password strength requirements (min 8 chars, numbers, special chars)
  - Widget: PasswordInput with Bootstrap styling
  - Help Text: Displays password requirements

- **password2**: CharField (required)
  - Validation: Must match password1
  - Widget: PasswordInput with Bootstrap styling
  - Error Message: "Passwords do not match" if different

### Validation Methods
```python
def clean_email(self):
    # Ensures email uniqueness
    # Prevents duplicate account registration
    
def clean_password2(self):
    # Verifies password confirmation matches
    # Provides user-friendly error messages
```

### Usage Example
```python
# In views.py - register view
form = CustomUserCreationForm(request.POST)
if form.is_valid():
    user = form.save()  # Saves user with hashed password
    login(request, user)
```

### Bootstrap Integration
- All fields use `form-control` class
- Error messages display with Bootstrap styling
- Form submission button uses `btn btn-primary`

---

## UserProfileForm

### Purpose
Used for updating user profile information including picture upload.

### Fields
- **bio**: CharField (optional)
  - Max Length: 500 characters
  - Widget: Textarea (4 rows)
  - Placeholder: "Tell us about yourself..."
  - Validation: Max 500 characters

- **location**: CharField (optional)
  - Max Length: 100 characters
  - Widget: TextInput
  - Placeholder: "City, Country"
  - Validation: Max 100 characters

- **website**: URLField (optional)
  - Validation: Valid URL format
  - Widget: URLInput
  - Placeholder: "https://example.com"
  - Error Message: "Enter a valid URL" if invalid

- **profile_picture**: ImageField (optional)
  - Accepted Formats: JPG, PNG, GIF
  - Max Size: 5MB (recommended)
  - Widget: FileInput with Bootstrap styling
  - Help Text: "Upload profile picture (max 5MB)"

### Validation Methods
```python
def clean_website(self):
    # Validates URL format if provided
    # Ensures website is accessible format
    
def clean_profile_picture(self):
    # Validates image file
    # Checks file size and format
```

### Usage Example
```python
# In views.py - profile view
form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
if form.is_valid():
    form.save()  # Updates profile with image
```

### Bootstrap Integration
- All fields use `form-control` class
- File input has custom styling
- Pre-fills current profile data
- Shows current profile picture if exists

---

## PostForm

### Purpose
Used for creating and updating blog posts with comprehensive validation.

### Fields
- **title**: CharField (required)
  - Max Length: 200 characters
  - Min Length: 3 characters
  - Widget: TextInput
  - Placeholder: "Enter post title..."
  - Help Text: "Maximum 200 characters (required)"
  - Validation:
    - Cannot be empty
    - Must be 3-200 characters
    - No invalid characters: `< > { }`

- **content**: TextField (required)
  - Min Length: 10 characters
  - Widget: Textarea (10 rows)
  - Placeholder: "Write your post content here..."
  - Help Text: "Tell your story... (minimum 10 characters required)"
  - Validation:
    - Cannot be empty
    - Must be at least 10 characters

### Validation Methods
```python
def clean_title(self):
    # Validates title
    # Checks length: 3-200 chars
    # Prevents special characters: < > { }
    # Strips whitespace automatically
    # Returns: Cleaned title string
    
def clean_content(self):
    # Validates content
    # Checks minimum 10 characters
    # Strips whitespace automatically
    # Returns: Cleaned content string
    
def clean(self):
    # Overall form validation
    # Ensures content is more than just title
    # Prevents identical title/content
    # Returns: Cleaned data or raises ValidationError
```

### Author Assignment
**Important**: Author is **NOT** a field in PostForm. It's automatically set in the view:

```python
# In PostCreateView
def form_valid(self, form):
    form.instance.author = self.request.user  # Auto-set
    return super().form_valid(form)
```

This prevents users from manipulating post ownership.

### Usage Example
```python
# In views.py - PostCreateView
form = PostForm(request.POST)
if form.is_valid():
    post = form.save(commit=False)
    post.author = request.user  # Set author
    post.save()  # Save post
```

### Bootstrap Integration
- Title field: TextInput with `form-control` class
- Content field: Textarea with `form-control` class
- Both fields have Bootstrap styling
- Error messages display with appropriate styling
- Form includes CSRF token protection

### Validation Example
```python
# Valid post
title = "My First Blog Post"
content = "This is a well-written blog post about Django development."

# Invalid posts
title = "AB"  # Too short
content = "Short"  # Too short
title = "<script>alert('XSS')</script>"  # Invalid characters
```

---

## PostSearchForm

### Purpose
Used for searching blog posts by title, content, or author.

### Fields
- **q**: CharField (optional)
  - Max Length: 200 characters
  - Min Length: 2 characters (if provided)
  - Widget: TextInput
  - Placeholder: "Search by title or content..."
  - Label: "Search Posts"
  - Validation:
    - If provided, minimum 2 characters
    - Maximum 200 characters
    - Empty string allowed (no search)

### Search Scope
The search queries against:
- Post **title** (case-insensitive)
- Post **content** (case-insensitive)
- Post **author username** (case-insensitive)

### Usage Example
```python
# In views.py - PostListView
search_query = self.request.GET.get('q', '').strip()
if search_query:
    queryset = queryset.filter(
        Q(title__icontains=search_query) |
        Q(content__icontains=search_query) |
        Q(author__username__icontains=search_query)
    )
```

### URL Example
```
# No search
/blog/

# Search for posts
/blog/?q=django

# Search with other filters
/blog/?q=django&sort_by=newest
```

### Bootstrap Integration
- Single search input with `form-control` class
- Quick search interface in post list
- Real-time form submission (GET request)

---

## PostFilterForm

### Purpose
Used for filtering and sorting blog posts by publication date or title.

### Fields
- **sort_by**: ChoiceField (optional)
  - Default: "newest"
  - Widget: Select dropdown with `form-control` class
  - Choices:
    1. **newest**: "Newest First" (default, `-published_date`)
    2. **oldest**: "Oldest First" (`published_date`)
    3. **title_asc**: "Title A-Z" (`title`)
    4. **title_desc**: "Title Z-A" (`-title`)
  - Validation: Must be one of valid choices

### Validation Methods
```python
def clean_sort_by(self):
    # Ensures sort choice is valid
    # Prevents SQL injection via choice injection
    # Only allows predefined choices
```

### Usage Example
```python
# In views.py - PostListView
sort_by = self.request.GET.get('sort_by', 'newest')
if sort_by == 'oldest':
    queryset = queryset.order_by('published_date')
elif sort_by == 'title_asc':
    queryset = queryset.order_by('title')
elif sort_by == 'title_desc':
    queryset = queryset.order_by('-title')
else:  # default 'newest'
    queryset = queryset.order_by('-published_date')
```

### URL Example
```
# Newest first (default)
/blog/

# Oldest first
/blog/?sort_by=oldest

# Title A-Z
/blog/?sort_by=title_asc

# Combined with search
/blog/?q=django&sort_by=title_desc
```

### Bootstrap Integration
- Dropdown select with `form-control` class
- Clean, intuitive filter interface
- Combines with search form

---

## Form Security

### CSRF Protection
All forms include CSRF token protection:
```html
{% csrf_token %}
```

This prevents cross-site request forgery attacks. The Django middleware:
1. Generates unique token per session
2. Validates token on form submission
3. Rejects requests without valid token

### Password Security
**CustomUserCreationForm** uses:
- PBKDF2 hashing algorithm
- 600,000+ iterations per password
- Django's built-in validators:
  - Minimum 8 characters
  - Cannot be all numeric
  - Cannot match username
  - Validated against common passwords database

### Input Validation
All forms validate input to prevent:
- XSS (Cross-Site Scripting): Special characters filtered
- SQL Injection: Django ORM parameterized queries
- Invalid data types: Field type validation
- Buffer overflow: Max length enforcement

### File Upload Security
**UserProfileForm** validates image uploads:
- File type checking (only images)
- File size limits
- Virus scanning (optional via external service)
- File renamed on upload (prevents path traversal)

---

## Validation Strategies

### Field-Level Validation
Each form field validates:
```python
class PostForm(forms.ModelForm):
    def clean_title(self):
        title = self.cleaned_data.get('title')
        # Field-level validation
        # Custom error messages
        return cleaned_title
```

### Form-Level Validation
After all fields validate:
```python
def clean(self):
    cleaned_data = super().clean()
    # Cross-field validation
    # Complex business logic
    return cleaned_data
```

### Model-Level Validation
Forms inherit from models:
```python
class PostForm(forms.ModelForm):
    class Meta:
        model = Post  # Inherits model validation
```

### Validation Error Messages
User-friendly error messages:
- "Post title must be at least 3 characters long."
- "Post content cannot be empty."
- "Enter a valid email address."
- "Passwords do not match."

---

## Form Testing

### Manual Testing Checklist

#### PostForm Creation
- [ ] Create post with valid title (3-200 chars) and content (10+ chars)
- [ ] Attempt to create with title < 3 chars (should fail)
- [ ] Attempt to create with content < 10 chars (should fail)
- [ ] Attempt to create with special characters in title (should fail)
- [ ] Verify author auto-sets to current user
- [ ] Verify published_date auto-sets to current time

#### PostForm Update
- [ ] Update post as author (should succeed)
- [ ] Attempt to update as non-author (should fail with 403)
- [ ] Update with empty title (should fail)
- [ ] Update with empty content (should fail)
- [ ] Verify changes save correctly

#### PostSearchForm
- [ ] Search for post by title (should find)
- [ ] Search for post by content (should find)
- [ ] Search for post by author username (should find)
- [ ] Search with empty query (should show all)
- [ ] Search with < 2 chars (should fail validation)
- [ ] Search with > 200 chars (should fail validation)

#### PostFilterForm
- [ ] Sort posts newest first (default)
- [ ] Sort posts oldest first
- [ ] Sort posts by title A-Z
- [ ] Sort posts by title Z-A
- [ ] Attempt invalid sort option (should fail)
- [ ] Combine search with sort

#### CustomUserCreationForm
- [ ] Register with valid username, email, password
- [ ] Attempt duplicate email (should fail)
- [ ] Attempt weak password (should fail)
- [ ] Attempt password mismatch (should fail)
- [ ] Verify user auto-creates UserProfile via signal

#### UserProfileForm
- [ ] Update bio (up to 500 chars)
- [ ] Update location (up to 100 chars)
- [ ] Update website with valid URL
- [ ] Update with invalid URL (should fail)
- [ ] Upload profile picture (JPG, PNG, GIF)
- [ ] Attempt upload oversized file (should fail)

### Automated Testing Example
```python
# Test file: blog/tests.py
class PostFormTestCase(TestCase):
    def test_post_form_valid(self):
        form_data = {
            'title': 'Test Post',
            'content': 'This is a test post content.'
        }
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_post_form_invalid_title(self):
        form_data = {
            'title': 'AB',  # Too short
            'content': 'This is a test post content.'
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
```

---

## Form Integration in Views

### PostListView
- **Forms Used**: PostSearchForm, PostFilterForm
- **GET Parameters**: ?q=search&sort_by=newest
- **Context Variables**:
  - `search_form`: PostSearchForm instance
  - `filter_form`: PostFilterForm instance
  - `search_query`: Current search term
  - `posts`: Paginated, filtered queryset

### PostCreateView
- **Form Used**: PostForm
- **Auto-Sets**: author=request.user
- **Redirect**: to post_detail on success
- **Permissions**: LoginRequiredMixin required

### PostUpdateView
- **Form Used**: PostForm
- **Permission**: UserPassesTestMixin (user == post.author)
- **Redirect**: to post_detail on success
- **Permissions**: LoginRequiredMixin + UserPassesTestMixin

### PostDetailView
- **Forms Used**: None (display only)
- **Context**: Full post with author info

### PostDeleteView
- **Form Used**: Confirmation form (internal)
- **Permission**: UserPassesTestMixin (user == post.author)
- **Redirect**: to post_list on success

---

## Best Practices

1. **Always validate on both client and server side**
2. **Include CSRF tokens on all POST/PUT/DELETE forms**
3. **Use form.is_valid() before form.save()**
4. **Provide user-friendly error messages**
5. **Never trust form data - always validate**
6. **Use ModelForm when possible for automatic validation**
7. **Test forms with invalid data**
8. **Keep sensitive logic out of forms (auth in views)**
9. **Use Bootstrap classes for consistent styling**
10. **Document custom validation methods**

---

## Troubleshooting

### Form Not Validating
1. Check clean_* methods for exceptions
2. Verify field types match expected data
3. Check CSRF token presence on POST
4. Review error messages: `form.errors`

### CSRF Token Errors
1. Ensure `{% csrf_token %}` in form
2. Check middleware: `django.middleware.csrf.CsrfViewMiddleware`
3. Verify session middleware enabled
4. Check cookie settings in settings.py

### Author Not Set Correctly
1. Verify view sets `form.instance.author = request.user`
2. Check author field not in form.Meta.fields
3. Verify LoginRequiredMixin applied
4. Test with authenticated user

### Search Not Working
1. Check Q() import: `from django.db.models import Q`
2. Verify search_query in get_queryset()
3. Test with different search terms
4. Check queryset ordering

---

## Future Enhancements

Potential form improvements:
1. Rich text editor (TinyMCE, CKEditor)
2. Tag/Category selection
3. Post scheduling (publish_date selection)
4. Markdown preview
5. Auto-save drafts
6. Image upload within posts
7. Social media sharing buttons
8. Comment forms for posts
9. Post rating/voting forms
10. Advanced search filters

---

## Contact & Support

For questions about form configuration:
- Review comments in blog/forms.py
- Check model definitions in blog/models.py
- Reference validation tests in blog/tests.py
- Consult Django Forms documentation

---

*Last Updated: 2024*
*Django Version: 6.0.1*
*Python Version: 3.14+*
