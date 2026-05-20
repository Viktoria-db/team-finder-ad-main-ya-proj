from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from users.avatar import generate_avatar_file
from users.managers import UserManager


class Skill(models.Model):
    name = models.CharField(max_length=124, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to="avatars/")
    phone = models.CharField(max_length=12)
    github_url = models.URLField(blank=True)
    about = models.TextField(blank=True, max_length=256)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    skills = models.ManyToManyField(Skill, related_name="users", blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname", "phone"]

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new and not self.avatar:
            self.avatar = generate_avatar_file(self.name)
        super().save(*args, **kwargs)
