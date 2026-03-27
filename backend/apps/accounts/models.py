from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'superadmin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('public', 'Public'),
        ('admin', 'Administrateur Partenaire'),
        ('superadmin', 'Super Administrateur'),
    ]

    PARTNER_TYPE_CHOICES = [
        ('notaire', 'Notaire'),
        ('universite', 'Université'),
        ('entreprise', 'Entreprise'),
        ('gouvernement', 'Gouvernement'),
        ('autre', 'Autre'),
    ]

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='public')
    partner_type = models.CharField(max_length=30, choices=PARTNER_TYPE_CHOICES, blank=True, null=True)
    organization_name = models.CharField(max_length=200, blank=True, null=True)
    organization_logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'Utilisateur'

    def __str__(self):
        return f"{self.full_name} ({self.role})"

    @property
    def is_superadmin(self):
        return self.role == 'superadmin'

    @property
    def is_admin_partner(self):
        return self.role == 'admin'
