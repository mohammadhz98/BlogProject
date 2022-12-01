from django.db import models
from django.conf import settings

# Create your models here.
class Member(models.Model):
    is_writer = models.BooleanField(default=False)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.user.username


class Guest(models.Model):
    full_name = models.CharField(max_length=40)
    email = models.EmailField(unique=True)

    def __str__(self) -> str:
        return self.email


class Post(models.Model):
    STATUS_PUBLISH = 'P'
    STATUS_DELETE = 'D'
    STATUS_WAIT = 'W'

    STATUS_CHOICES = [
        (STATUS_PUBLISH, 'Publish'),
        (STATUS_DELETE, 'Delete'),
        (STATUS_WAIT, 'Wait'),
    ]

    title = models.CharField(max_length=250)
    short_description = models.TextField(max_length=600)
    description = models.TextField()
    image = models.ImageField(upload_to="blog/post/images")
    slug = models.SlugField(unique=True, null=False)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_WAIT)
    writer = models.ForeignKey(Member, on_delete=models.PROTECT)
    tags = models.ManyToManyField("Tag", blank=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="likes")
    category = models.ForeignKey("Category", on_delete=models.PROTECT, related_name="posts") 
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    delete_at = models.DateTimeField(null=True)

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    STATUS_PUBLISH = 'P'
    STATUS_DELETE = 'D'
    STATUS_WAIT = 'W'

    STATUS_CHOICES = [
        (STATUS_PUBLISH, 'Publish'),
        (STATUS_DELETE, 'Delete'),
        (STATUS_WAIT, 'Wait'),
    ]

    text = models.TextField()
    user = models.ForeignKey(Member, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_WAIT)

    def __str__(self) -> str:
        return f"user :<{self.member.user.username}> comment on post <{self.post.title[:10]} ....>"


class Category(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField()

    def __str__(self) -> str:
        return self.title


class Tag(models.Model):
    title = models.CharField(max_length=50, unique=True)
    
    def __str__(self) -> str:
        return self.title


class Header(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    image = models.ImageField(upload_to="blog/header/images")

    def __str__(self) -> str:
        return self.title