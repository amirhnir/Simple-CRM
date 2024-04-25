from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CompanyUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=11, unique=True)
    email = models.CharField(max_length=100 ,default= '')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = [ 'name','email']

    def save(self, *args, **kwargs):
        self.date_created = timezone.now()
        super(CompanyUser, self).save(*args, **kwargs)

    def __str__(self):
        return f"CompanyUser: {self.name} - {self.phone}"


class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=11)
    date_created = models.DateField(auto_now_add=True)
    company_user = models.ForeignKey(CompanyUser, on_delete=models.CASCADE, related_name='customers')

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return f"Customer: {self.name} - {self.phone}"


class Label(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(CompanyUser, on_delete=models.CASCADE, related_name='labels')
    customers = models.ManyToManyField(Customer, related_name='labels')

    def __str__(self):
        return f"{self.name}"


class Note(models.Model):
    description = models.TextField()
    date_created = models.DateField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notes')

    def __str__(self):
        return f"Note: {self.description[:50]}"
