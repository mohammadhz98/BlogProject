from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.response import Response
from .models import Member, Post, Comment, Category, Tag, Header
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import transaction
import re
from rest_framework.authtoken.models import Token
from . import models


class UserWriteSerializer(serializers.ModelSerializer):
    #todo: Create user must be by email or number verification
    #todo: Create user must have google sign in

    class Meta:
        model = get_user_model()
        fields = ('id', "username", "password", "first_name", "last_name", "email", "auth_token")
        extra_kwargs = {
            'password': {'write_only': True},
            'auth_token': {'read_only': True}
        }

        token = serializers.StringRelatedField(source='auth_token')
    
    @transaction.atomic
    def save(self, **kwargs):
        encryptedpassword = make_password(self.validated_data['password'])     
        self.validated_data['password'] = encryptedpassword
        return super().save(**kwargs)

    @transaction.atomic
    def create(self, validated_data):  
        validated_data["is_staff"] = False
        validated_data["is_active"] = True
        user = super().create(validated_data)
        return user


class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', "username", "first_name", "last_name", "email", "active", "admin")

    admin = serializers.BooleanField(source="is_staff")
    active = serializers.BooleanField(source="is_active")

        
class MemberWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('id', "address", "phone")

    @transaction.atomic
    def save(self, **kwargs):
        self.instance
        self.validated_data['user_id'] = self.instance.user.id
        return super().save(**kwargs)

    @transaction.atomic
    def create(self, validated_data):
        validated_data["is_writer"] = False
        member = super().create(validated_data)
        return member


class MemberReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('id', "address", "phone", "user", "writer")
    
    user = UserReadSerializer()
    writer = serializers.BooleanField(source="is_writer")


class PostWriteSerializer(serializers.ModelSerializer):
    #todo: writer can write post
    #todo: writer can change or delete own post

    class Meta:
        model = Post
        fields = ["id", "title", "short_description", "description", "image", "tags", "category" ]

    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())

    @transaction.atomic
    def create(self, validated_data):
        slug = re.sub(' ',  '-', validated_data["title"])
        if Post.objects.filter(slug=slug):
            raise serializers.ValidationError(f"post with slug `{slug}` is already exists.")
        validated_data["slug"] = slug
        validated_data["writer"] = self.context.get('request').user.member
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
    class Meta:
        model = Comment
        fields = ("id", "text", "email")
    
    email = serializers.EmailField(required=False)

    @transaction.atomic
    def create(self, validated_data):
        validated_data['post_id'] = self.context['post_id']
        validated_data["status"] = "W"

        user = self.context['request'].user
        if user and hasattr(user, 'email') :
            validated_data["email"] = user.email
        elif self.validated_data.get('email', None):
            validated_data["email"] = self.validated_data.get('email', "eror@gmail.com")
        else:
            raise serializers.ValidationError('Email khod ra vared konid!')

        comment = super().create(validated_data)
        return comment


class CommentReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', "text", "post", "user", "status")

    user = serializers.EmailField(source='email')
    post = serializers.HyperlinkedRelatedField(view_name="post-detail", read_only=True)
    status = serializers.CharField(source='get_status_display')


class CategoryWriteSerializer(serializers.ModelSerializer):

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
    class Meta:
        model = Tag
        fields = ('id', "title")


class HeaderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Header
        fields = ('id', "title", "description", "image")