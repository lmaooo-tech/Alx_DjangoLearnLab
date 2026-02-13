from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import Http404
from .forms import CustomUserCreationForm, UserProfileForm, PostForm, PostSearchForm, PostFilterForm
from .models import Post, UserProfile
from django.db.models import Q


def register(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in immediately after registration
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Django Blog.')
            return redirect('profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'blog/register.html', {'form': form})


def login_view(request):
    """Handle user login using Django's built-in authentication"""
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_page = request.GET.get('next', 'profile')
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'blog/login.html')


def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required(login_url='login')
def profile(request):
    """Display and manage user profile with extended fields"""
    try:
        user_profile = request.user.profile
    except:
        # Create profile if it doesn't exist
        from .models import UserProfile
        user_profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserProfileForm(instance=user_profile)
    
    context = {
        'form': form,
        'user_profile': user_profile,
    }
    return render(request, 'blog/profile.html', context)


# ============================================================================
# Blog Post CRUD Views (Class-Based Views)
# ============================================================================

class PostListView(ListView):
    """Display all blog posts with search and filter functionality"""
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    ordering = ['-published_date']
    
    def get_queryset(self):
        """Get queryset with search and filter support"""
        queryset = Post.objects.all().order_by('-published_date')
        
        # Search functionality
        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(author__username__icontains=search_query)
            )
        
        # Sort/Filter functionality
        sort_by = self.request.GET.get('sort_by', 'newest')
        if sort_by == 'oldest':
            queryset = queryset.order_by('published_date')
        elif sort_by == 'title_asc':
            queryset = queryset.order_by('title')
        elif sort_by == 'title_desc':
            queryset = queryset.order_by('-title')
        else:  # default to 'newest'
            queryset = queryset.order_by('-published_date')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'All Blog Posts'
        context['search_form'] = PostSearchForm(self.request.GET or None)
        context['filter_form'] = PostFilterForm(self.request.GET or None)
        context['search_query'] = self.request.GET.get('q', '').strip()
        return context


class PostDetailView(DetailView):
    """Display a single blog post"""
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['title'] = post.title
        context['can_edit'] = self.request.user == post.author
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Allow authenticated users to create new blog posts
    
    Permission Requirements:
    - User must be authenticated (LoginRequiredMixin)
    - Anonymous users redirected to login page
    
    Features:
    - Author auto-set to current user
    - Success message displayed
    - Redirects to post detail on success
    """
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    login_url = 'blog:login'
    redirect_field_name = 'next'
    
    def form_valid(self, form):
        """Set the author to the current user before saving"""
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Post created successfully!')
        return response
    
    def get_success_url(self):
        """Redirect to the new post detail page"""
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Create'
        return context


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Allow post authors to edit their posts
    
    Permission Requirements:
    - User must be authenticated (LoginRequiredMixin)
    - User must be the post author (UserPassesTestMixin)
    - Non-authors receive 403 Forbidden
    - Anonymous users redirected to login
    
    Features:
    - Form pre-filled with current data
    - Same validation as create
    - Success message displayed
    - Redirects to post detail on success
    """
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    login_url = 'blog:login'
    pk_url_kwarg = 'pk'
    
    def test_func(self):
        """Check if user is the post author - required by UserPassesTestMixin"""
        try:
            post = self.get_object()
            is_author = self.request.user == post.author
            if not is_author:
                messages.warning(
                    self.request,
                    'You can only edit your own posts.'
                )
            return is_author
        except Post.DoesNotExist:
            return False
    
    def handle_no_permission(self):
        """Redirect with error message if user is not the author"""
        try:
            post = self.get_object()
            messages.error(
                self.request,
                'You do not have permission to edit this post.'
            )
            return redirect('blog:post_detail', pk=post.pk)
        except Post.DoesNotExist:
            messages.error(self.request, 'Post not found.')
            return redirect('blog:post_list')
    
    def form_valid(self, form):
        """Process form submission"""
        response = super().form_valid(form)
        messages.success(self.request, 'Post updated successfully!')
        return response
    
    def get_success_url(self):
        """Redirect to the updated post detail page"""
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Update'
        return context


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Allow post authors to delete their posts
    
    Permission Requirements:
    - User must be authenticated (LoginRequiredMixin)
    - User must be the post author (UserPassesTestMixin)
    - Non-authors receive 403 Forbidden
    - Anonymous users redirected to login
    
    Features:
    - GET displays confirmation page with post preview
    - POST processes deletion
    - Success message displayed
    - Redirects to post list on success
    - Post cannot be recovered after deletion
    """
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    login_url = 'blog:login'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('blog:post_list')
    
    def test_func(self):
        """Check if user is the post author - required by UserPassesTestMixin"""
        try:
            post = self.get_object()
            is_author = self.request.user == post.author
            if not is_author:
                messages.warning(
                    self.request,
                    'You can only delete your own posts.'
                )
            return is_author
        except Post.DoesNotExist:
            return False
    
    def handle_no_permission(self):
        """Redirect with error message if user is not the author"""
        try:
            post = self.get_object()
            messages.error(
                self.request,
                'You do not have permission to delete this post.'
            )
            return redirect('blog:post_detail', pk=post.pk)
        except Post.DoesNotExist:
            messages.error(self.request, 'Post not found.')
            return redirect('blog:post_list')
    
    def delete(self, request, *args, **kwargs):
        """Process deletion with success message"""
        post_title = self.get_object().title
        response = super().delete(request, *args, **kwargs)
        messages.success(
            request,
            f'Post "{post_title}" deleted successfully!'
        )
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Post'
        return context


class UserPostsView(ListView):
    """Display all posts by a specific user"""
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 10
    pk_url_kwarg = 'pk'
    
    def get_queryset(self):
        """Filter posts by the specified user"""
        user_id = self.kwargs['pk']
        return Post.objects.filter(author_id=user_id).order_by('-published_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = get_object_or_404(User, pk=self.kwargs['pk'])
        context['author'] = author
        context['title'] = f'Posts by {author.get_full_name or author.username}'
        return context
