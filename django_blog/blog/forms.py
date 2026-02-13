from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Post, Comment, Tag


class CustomUserCreationForm(UserCreationForm):
    """Extended user registration form with email field"""
    email = forms.EmailField(
        required=True,
        help_text='Required. Enter a valid email address.'
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        help_text='Optional.'
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        help_text='Optional.'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        """Validate that email is unique"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already registered.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=150, required=False)

    class Meta:
        model = UserProfile
        fields = ('bio', 'profile_picture', 'location', 'website')
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Tell us about yourself...'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your location'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourwebsite.com'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add current user's email and name fields with form-control class
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
        
        # Add form-control class to all fields
        for field_name, field in self.fields.items():
            if field_name in ['email', 'first_name', 'last_name']:
                field.widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        """Validate that email is unique (excluding current user)"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.user.pk).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        # Update the related user object
        profile.user.email = self.cleaned_data['email']
        profile.user.first_name = self.cleaned_data.get('first_name', '')
        profile.user.last_name = self.cleaned_data.get('last_name', '')
        
        if commit:
            profile.user.save()
            profile.save()
        return profile


class PostForm(forms.ModelForm):
    """Form for creating and updating blog posts with comprehensive validation"""
    
    tags = forms.CharField(
        max_length=500,
        required=False,
        label='Tags',
        help_text='Enter tags separated by commas (e.g., "Django, Python, Web Development")',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter tags separated by commas...',
            'id': 'id_tags',
            'autocomplete': 'off'
        })
    )
    
    class Meta:
        model = Post
        fields = ('title', 'content')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post title...',
                'maxlength': '200',
                'id': 'id_title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your post content here...',
                'rows': 10,
                'id': 'id_content'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom attributes
        self.fields['title'].label = 'Post Title'
        self.fields['content'].label = 'Post Content'
        
        # Add help texts with character limits
        self.fields['title'].help_text = 'Maximum 200 characters (required)'
        self.fields['content'].help_text = 'Tell your story... (minimum 10 characters required)'
        
        # Add required field markers
        self.fields['title'].required = True
        self.fields['content'].required = True
        
        # Populate tags field if editing an existing post
        if self.instance and self.instance.pk:
            tag_names = ', '.join([tag.name for tag in self.instance.tags.all()])
            self.fields['tags'].initial = tag_names
    
    def clean_title(self):
        """Validate post title"""
        title = self.cleaned_data.get('title')
        if not title:
            raise forms.ValidationError('Post title cannot be empty.')
        
        title = title.strip()
        
        if len(title) < 3:
            raise forms.ValidationError('Post title must be at least 3 characters long.')
        
        if len(title) > 200:
            raise forms.ValidationError('Post title cannot exceed 200 characters.')
        
        # Check for special characters
        if any(char in title for char in ['<', '>', '{', '}']):
            raise forms.ValidationError('Post title contains invalid characters.')
        
        return title
    
    def clean_content(self):
        """Validate post content"""
        content = self.cleaned_data.get('content')
        if not content:
            raise forms.ValidationError('Post content cannot be empty.')
        
        content = content.strip()
        
        if len(content) < 10:
            raise forms.ValidationError('Post content must be at least 10 characters long.')
        
        # Warn if content is very short (but allow it)
        if len(content) < 50:
            pass  # Allow but could be enhanced with a warning
        
        return content
    
    def clean_tags(self):
        """Validate and process tags"""
        tags_str = self.cleaned_data.get('tags', '').strip()
        
        if not tags_str:
            # Tags are optional
            return []
        
        # Split tags by comma and clean up
        tag_names = [tag.strip() for tag in tags_str.split(',')]
        tag_names = [tag for tag in tag_names if tag]  # Remove empty strings
        
        # Validate tag count
        if len(tag_names) > 10:
            raise forms.ValidationError('A post can have a maximum of 10 tags.')
        
        # Validate individual tag names
        for tag_name in tag_names:
            if len(tag_name) < 2:
                raise forms.ValidationError(f'Tag "{tag_name}" is too short (minimum 2 characters).')
            if len(tag_name) > 50:
                raise forms.ValidationError(f'Tag "{tag_name}" is too long (maximum 50 characters).')
            if any(char in tag_name for char in ['<', '>', '{', '}']):
                raise forms.ValidationError(f'Tag "{tag_name}" contains invalid characters.')
        
        return tag_names
    
    def clean(self):
        """Overall form validation"""
        cleaned_data = super().clean()
        title = cleaned_data.get('title', '').strip()
        content = cleaned_data.get('content', '').strip()
        
        # Ensure title and content are different
        if title.lower() == content[:len(title)].lower():
            raise forms.ValidationError('Post content should be more than just the title.')
        
        return cleaned_data
    
    def save_tags(self, post_instance):
        """
        Create or retrieve tags and associate them with the post.
        This method should be called from the view after saving the post instance.
        
        Args:
            post_instance: The Post model instance to associate tags with
        """
        tags_str = self.cleaned_data.get('tags', '').strip()
        
        # Clear existing tags
        post_instance.tags.clear()
        
        if not tags_str:
            return
        
        # Parse tags
        tag_names = [tag.strip() for tag in tags_str.split(',')]
        tag_names = [tag for tag in tag_names if tag]
        
        # Create or retrieve tags and associate with post
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'slug': tag_name.lower().replace(' ', '-')}
            )
            post_instance.tags.add(tag)
        
        return post_instance


class PostSearchForm(forms.Form):
    """Form for searching blog posts by title, content, and tags"""
    
    SEARCH_TYPE_CHOICES = [
        ('all', 'All Content (Title, Content, Tags)'),
        ('title', 'Title Only'),
        ('content', 'Content Only'),
        ('tags', 'Tags Only'),
        ('author', 'Author'),
    ]
    
    q = forms.CharField(
        max_length=200,
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter search term...',
            'id': 'search_query',
            'autocomplete': 'off'
        })
    )
    
    search_type = forms.ChoiceField(
        choices=SEARCH_TYPE_CHOICES,
        required=False,
        initial='all',
        label='Search In',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'search_type'
        })
    )
    
    tags = forms.CharField(
        max_length=300,
        required=False,
        label='Filter by Tags',
        help_text='Enter tag names separated by commas (e.g., "Django, Python")',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by tags (comma-separated)...',
            'id': 'search_tags',
            'autocomplete': 'off'
        })
    )
    
    def clean_q(self):
        """Validate search query"""
        query = self.cleaned_data.get('q', '').strip()
        if query and len(query) < 2:
            raise forms.ValidationError('Search query must be at least 2 characters long.')
        return query
    
    def clean_tags(self):
        """Validate tag input"""
        tags_str = self.cleaned_data.get('tags', '').strip()
        if not tags_str:
            return []
        
        # Split and validate tags
        tag_names = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        
        if len(tag_names) > 5:
            raise forms.ValidationError('You can filter by a maximum of 5 tags.')
        
        for tag_name in tag_names:
            if len(tag_name) < 2:
                raise forms.ValidationError(f'Tag "{tag_name}" is too short (minimum 2 characters).')
        
        return tag_names
    
    def clean_search_type(self):
        """Validate search type"""
        search_type = self.cleaned_data.get('search_type')
        valid_types = [choice[0] for choice in self.SEARCH_TYPE_CHOICES]
        if search_type and search_type not in valid_types:
            raise forms.ValidationError('Invalid search type.')
        return search_type


class PostFilterForm(forms.Form):
    """Form for filtering blog posts"""
    SORT_CHOICES = [
        ('newest', 'Newest First'),
        ('oldest', 'Oldest First'),
        ('title_asc', 'Title A-Z'),
        ('title_desc', 'Title Z-A'),
    ]
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='newest',
        label='Sort By',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'sort_by'
        })
    )
    
    def clean_sort_by(self):
        """Validate sort choice"""
        sort_by = self.cleaned_data.get('sort_by')
        valid_choices = [choice[0] for choice in self.SORT_CHOICES]
        if sort_by and sort_by not in valid_choices:
            raise forms.ValidationError('Invalid sort option.')
        return sort_by


class CommentForm(forms.ModelForm):
    """Form for creating and updating blog comments with validation"""
    
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your comment here...',
                'rows': 4,
                'id': 'id_content'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize field properties
        self.fields['content'].label = 'Your Comment'
        self.fields['content'].help_text = 'Share your thoughts... (minimum 3 characters required)'
        self.fields['content'].required = True
    
    def clean_content(self):
        """Validate comment content"""
        content = self.cleaned_data.get('content')
        
        if not content:
            raise forms.ValidationError('Comment cannot be empty.')
        
        content = content.strip()
        
        if len(content) < 3:
            raise forms.ValidationError('Comment must be at least 3 characters long.')
        
        if len(content) > 5000:
            raise forms.ValidationError('Comment cannot exceed 5000 characters.')
        
        return content
    
    def clean(self):
        """Overall form validation"""
        cleaned_data = super().clean()
        content = cleaned_data.get('content', '').strip()
        
        # Ensure content isn't just whitespace
        if not content:
            raise forms.ValidationError('Please write a meaningful comment.')
        
        return cleaned_data
