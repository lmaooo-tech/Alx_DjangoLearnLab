# Generated migration for posts app models

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(help_text='The content of the post', max_length=5000)),
                ('image', models.ImageField(blank=True, help_text='optional image for the post', null=True, upload_to='post_images/')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Timestamp when the post was created')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Timestamp when the post was last updated')),
                ('author', models.ForeignKey(help_text='The user who created this post', on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Post',
                'verbose_name_plural': 'Posts',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Timestamp when the like was created')),
                ('post', models.ForeignKey(help_text='The post that was liked', on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='posts.post')),
                ('user', models.ForeignKey(help_text='The user who liked the post', on_delete=django.db.models.deletion.CASCADE, related_name='likes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Like',
                'verbose_name_plural': 'Likes',
                'ordering': ['-created_at'],
                'unique_together': {('user', 'post')},
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(help_text='The content of the comment', max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Timestamp when the comment was created')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Timestamp when the comment was last updated')),
                ('author', models.ForeignKey(help_text='The user who created the comment', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(help_text='The post being commented on', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='posts.post')),
            ],
            options={
                'verbose_name': 'Comment',
                'verbose_name_plural': 'Comments',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['-created_at'], name='posts_post_created_idx'),
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['author', '-created_at'], name='posts_post_author_created_idx'),
        ),
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['post', '-created_at'], name='posts_comment_post_created_idx'),
        ),
    ]
