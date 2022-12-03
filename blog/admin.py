from django.urls import reverse
from django.contrib import admin
from django.http import HttpRequest
from django.utils.html import format_html, urlencode
from django.db.models.aggregates import Count
from . import models


@admin.register(models.Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['username', 'full_name', 'phone', 'address', 'is_writer', 'is_active']
    list_select_related = ['user']
    search_fields = [
        'user__username__istartswith',
        'user__first_name__istartswith',
        'user__last_name__istartswith',
        ]

    @admin.display(ordering='user__username')
    def username(self, member):
        return member.user.username

    @admin.display(ordering='user__first_name')
    def full_name(self, member):
        return f"{member.user.first_name} {member.user.last_name}" 


    @admin.display(ordering='user__is_active')
    def is_active(self, member):
        return member.user.is_active

    def __str__(self) -> str:
        return self.full_name


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    #todo: show image thumbnail
    #todo: click on status publish or delete post
    #todo: delete unnecessery fields
    list_display = ['title', 'short_description', 'image', 'writer', 'create_at', 'update_at', 'delete_at', 'status']
    list_select_related = ['writer']
    
    # Form 
    readonly_fields = ['create_at', 'update_at', 'delete_at']
    autocomplete_fields = ['writer']
    prepopulated_fields = {
        'slug' : ['title']
    }


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    #todo: slug must be prepopulated and read only
    list_display = ['title', 'slug', 'posts_count']
    
    prepopulated_fields = {
        'slug' : ['title']
    }

    @admin.display(ordering='posts_count')
    def posts_count(self, category):
        url = (reverse('admin:blog_post_changelist') 
        + '?' 
        + urlencode({
            'category__id' : str(category.id)
        }))
        return format_html('<a href="{}">{}</a>', url, category.posts_count)

    def get_queryset(self, request: HttpRequest):
        return super().get_queryset(request).annotate(posts_count=Count('posts'))


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user_username', 'post_slug', 'text', 'status']
    list_select_related = ['user', 'post']

    @admin.display(ordering='user__username')
    def user_username(self, comment):
        return comment.user.username

    @admin.display(ordering='post__slug')
    def post_slug(self, comment):
        return f"{comment.post.slug}" 


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Header)
class HeaderAdmin(admin.ModelAdmin):
    pass
