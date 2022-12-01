from django.views import View
from django.db.models import Q
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.exceptions import status
from rest_framework import viewsets
from rest_framework.decorators import action
from .models import Member, Guest, Post, Comment, Category, Tag, Header
from .serializers import UserWriteSerializer, UserReadSerializer, MemberWriteSerializer, MemberReadSerializer, GuestSerializer, PostWriteSerializer, PostReadSerializer, CommentWriteSerializer, CommentReadSerializer, CategoryWriteSerializer, CategoryReadSerializer, TagSerializer, HeaderSerializer


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    
    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserReadSerializer
        else:
            return UserWriteSerializer


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == "GET":
            return MemberReadSerializer
        return MemberWriteSerializer


@action(detail=False, methods=["GET", "PUT"])
def me(self, request):
    (member, created) = Member.objects.get_or_create(user_id=request.user.id)

    if request.method == 'GET':
        serializer = MemberReadSerializer(member)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = MemberReadSerializer(Member, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class GuestViewSet(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("writer").select_related("category").prefetch_related("tags").prefetch_related("likes").all()
    serializer_class = PostReadSerializer


    def get_serializer_class(self):
        if self.request.method == "GET":
            return PostReadSerializer
        return PostWriteSerializer


class CommentViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        if self.request.method == "GET":
            return Comment.objects.select_related("user").select_related("post").filter(post_id=self.kwargs['post_pk']).filter(Q(status=Comment.STATUS_PUBLISH) | Q(user_id=self.request.user.id))
        else:
            return Comment.objects.select_related("user").select_related("post").filter(post_id=self.kwargs['post_pk'])

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CommentReadSerializer
        return CommentWriteSerializer

    def get_serializer_context(self):
        return {'request':self.request, 'post_id':self.kwargs['post_pk']}
   

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryReadSerializer

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CategoryReadSerializer
        return CategoryWriteSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    

class HeaderViewSet(viewsets.ModelViewSet):
    queryset = Header.objects.all()
    serializer_class = HeaderSerializer
    