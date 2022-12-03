from django.urls import path, include
from . import views
from rest_framework_nested import routers 



router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'members', views.MemberViewSet, basename='member')
router.register(r'posts', views.PostViewSet, basename='post')
posts_router = routers.NestedDefaultRouter(router, r'posts', lookup='post')
posts_router.register(r'comments', views.CommentViewSet, basename="post-comments")
router.register(r'categories', views.CategoryViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'headers', views.HeaderViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('', include(posts_router.urls)),
    path('login/', views.auth.as_view(), name='login'),
    
]
