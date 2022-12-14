from django.views import View
from django.db.models import Q
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.models import AnonymousUser
from rest_framework.response import Response
from rest_framework.exceptions import status
from rest_framework import viewsets, mixins
from rest_framework.decorators import action, APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser, AllowAny 
from rest_framework.authtoken.models import Token
from . import models
from .serializers import UserWriteSerializer, UserReadSerializer, MemberWriteSerializer, MemberReadSerializer, PostWriteSerializer, PostReadSerializer, CommentWriteSerializer, CommentReadSerializer, CategoryWriteSerializer, CategoryReadSerializer, TagSerializer, HeaderSerializer
from .permissions import IsAdminOrReadOnly, IsAdminOrOwnUserOnly,  IsAdminOrOwnMemberOnly, IsPostWriterOrReadOnly, IsWriterOrReadOnly, IsUserOwner, IsMemberOwner, NotAllowAny

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):    
    queryset = get_user_model().objects.all()
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_anonymous:
            return get_user_model().objects.all()
        elif user.is_authenticated:
            return get_user_model().objects.filter(id=user.id)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserReadSerializer
        else:
            return UserWriteSerializer

    def get_permissions(self):
        if (self.request.method == 'POST') or self.request.user.is_staff:
            return [AllowAny(),]
        elif self.request.user.is_anonymous:
            return [NotAllowAny(),]
        else:
            return [IsUserOwner(),]


class MemberViewSet(viewsets.ModelViewSet):    

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_anonymous:
            return models.Member.objects.all()
        elif user.is_authenticated:
            return models.Member.objects.filter(user_id=user.id)
    
    def get_serializer_class(self):
        if self.request.method == "GET":
            return MemberReadSerializer
        return MemberWriteSerializer

    def get_permissions(self):
        if (self.request.method == 'POST') or self.request.user.is_anonymous:
            return [NotAllowAny(),]
        elif self.request.user.is_staff:
            return [AllowAny(),]
        else:
            return [IsMemberOwner(),]


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostReadSerializer

    permission_classes = [IsPostWriterOrReadOnly]

    def get_queryset(self):
        if self.request.method == "GET":
            return models.Post.objects.select_related("writer").select_related("category").prefetch_related("tags").prefetch_related("likes").filter(Q(status=models.Post.STATUS_PUBLISH) | Q(writer_id__user_id=self.request.user.id))
        else:
            return models.Post.objects.select_related("writer").select_related("category").prefetch_related("tags").prefetch_related("likes").filter()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return PostReadSerializer
        return PostWriteSerializer


class CommentViewSet(mixins.CreateModelMixin, 
                    mixins.RetrieveModelMixin, 
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    def get_queryset(self):
        if self.request.method == "GET" and self.request.user != AnonymousUser():
            return models.Comment.objects.select_related("post").filter(post_id=self.kwargs['post_pk']).filter(Q(status=models.Comment.STATUS_PUBLISH) | Q(email=self.request.user.email))
        elif self.request.method == "GET":
            return models.Comment.objects.select_related("post").filter(post_id=self.kwargs['post_pk']).filter(status=models.Comment.STATUS_PUBLISH)
        else:
            return models.Comment.objects.select_related("post").filter(post_id=self.kwargs['post_pk'])

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CommentReadSerializer
        return CommentWriteSerializer

    def get_serializer_context(self):
        return {'request':self.request, 'post_id':self.kwargs['post_pk']}
   

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = CategoryReadSerializer

    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CategoryReadSerializer
        return CategoryWriteSerializer


class TagViewSet(mixins.CreateModelMixin, 
                   mixins.RetrieveModelMixin, 
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = TagSerializer
    
    permission_classes = (IsWriterOrReadOnly, IsAdminUser)


class HeaderViewSet(viewsets.ModelViewSet):
    queryset = models.Header.objects.all()
    serializer_class = HeaderSerializer

    permission_classes = (IsAdminOrReadOnly,)
    

class auth(APIView):
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request):
        content =f"request.user : {request.user}    request.auth : {request.auth}"
        return Response(content)
    
    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            (token, _) = Token.objects.get_or_create(user=user)
            response = Response(f"{token.key}")
            response['headers'] = 'Authorization'
            return response
        return Response({'error':'eroor'})