from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import Member, Guest, Post, Comment, Category, Tag, Header
from django.contrib.auth import get_user_model
from django.db import transaction
import re

class UserWriteSerializer(serializers.ModelSerializer):
    #todo: Each user can write own object

    #todo: Create user must be by email or number verification

    #todo: Create user must have google sign in

    class Meta:
        model = get_user_model()
        fields = ('id', "username", "password", "first_name", "last_name", "email" )

    @transaction.atomic
    def create(self, validated_data):  
        encryptedpassword = make_password(validated_data['password'])
        
        validated_data['password'] = encryptedpassword
        validated_data["is_staff"] = False
        validated_data["is_active"] = True

        user = super().create(validated_data)
        return user


class UserReadSerializer(serializers.ModelSerializer):
    #todo: Just admin can see User list

    class Meta:
        model = get_user_model()
        fields = ('id', "username", "first_name", "last_name", "email", "active", "admin")

    admin = serializers.BooleanField(source="is_staff")
    active = serializers.BooleanField(source="is_active")

        
class MemberWriteSerializer(serializers.ModelSerializer):
    #todo: create member is based on user auth
    #todo: this permission must be just for own user

    class Meta:
        model = Member
        fields = ('id', "address", "phone", "user")
    
    @transaction.atomic
    def create(self, validated_data):
        validated_data["is_writer"] = False
        member = super().create(validated_data)
        return member
    

class MemberReadSerializer(serializers.ModelSerializer):
    #todo: create member is based on user auth
    #todo: this permission must be just for own user

    class Meta:
        model = Member
        fields = ('id', "address", "phone", "user", "writer")
    
    user = UserReadSerializer()
    writer = serializers.BooleanField(source="is_writer")


class GuestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Guest
        fields = ('id', "full_name", "email")


class PostWriteSerializer(serializers.ModelSerializer):
    #todo: writer can write post
    #todo: writer can change or delete own post

    class Meta:
        model = Post
        fields = ["id", "title", "short_description", "description", "image", "writer", "tags", "category" ]


    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())

    @transaction.atomic
    def create(self, validated_data):
        slug = re.sub(' ',  '-', validated_data["title"])
        if Post.objects.filter(slug=slug):
            raise serializers.ValidationError(f"post with slug `{slug}` is already exists.")
        validated_data["slug"] = slug

        validated_data["status"] = "W"

        tags = validated_data.pop('tags', [])
        post = super().create(validated_data)

        if tags:
            post.tags.set(tags)

        return post


class PostReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "title", "short_description", "description", "image", "slug", "status", "writer", "tags", "likes", "category" ]


    status = serializers.CharField(source='get_status_display')
    writer = MemberReadSerializer()
    tags = serializers.StringRelatedField(many=True)
    likes = serializers.StringRelatedField(many=True)
    category = serializers.HyperlinkedRelatedField(view_name='category-detail', read_only=True)


class CommentWriteSerializer(serializers.ModelSerializer):
    #todo: comment must be write based on user or guest
    class Meta:
        model = Comment
        fields = ("id", "text", "user")
    
    @transaction.atomic
    def create(self, validated_data):
        validated_data['post_id'] = self.context['post_id']
        validated_data["status"] = "W"
        comment = super().create(validated_data)
        return comment


class CommentReadSerializer(serializers.ModelSerializer):
    #todo: users can see just published comments or own comment
    class Meta:
        model = Comment
        fields = ('id', "text", "post", "user", "status")

    user = serializers.HyperlinkedRelatedField(view_name="member-detail", read_only=True)
    post = serializers.HyperlinkedRelatedField(view_name="post-detail", read_only=True)
    status = serializers.CharField(source='get_status_display')


class CategoryWriteSerializer(serializers.ModelSerializer):
    #todo: just admin can change categories

    class Meta:
        model = Category
        fields = ('id', "title")

    @transaction.atomic
    def create(self, validated_data):
        slug = re.sub(' ',  '-', validated_data["title"])
        if Category.objects.filter(slug=slug):
            raise serializers.ValidationError(f"category with slug `{slug}` is already exists.")
        validated_data["slug"] = slug

        category = super().create(validated_data)
        return category


class CategoryReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', "title", "slug")


class TagSerializer(serializers.ModelSerializer):
    #todo: just writer can change tags
    class Meta:
        model = Tag
        fields = ('id', "title")


class HeaderSerializer(serializers.ModelSerializer):
    #todo: just admin can change header

    class Meta:
        model = Header
        fields = ('id', "title", "description", "image")