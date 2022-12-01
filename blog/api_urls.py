from django.urls import path, include
from . import views
from rest_framework_nested import routers 



router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'members', views.MemberViewSet)
router.register(r'guests', views.GuestViewSet)
router.register(r'posts', views.PostViewSet)
posts_router = routers.NestedDefaultRouter(router, r'posts', lookup='post')
posts_router.register(r'comments', views.CommentViewSet, basename="post-comments")
router.register(r'categories', views.CategoryViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'headers', views.HeaderViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('', include(posts_router.urls)),
    path('auth/', include("django.contrib.auth.urls")),
    
]
