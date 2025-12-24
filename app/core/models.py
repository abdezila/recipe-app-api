"""Database models"""
import uuid
import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

class UserManager(BaseUserManager):
    """Manager for users."""
    def create_user(self, email, password, **extra_fields):
        """Create,save and return a new user.""" 
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email =self.normalize_email(email) , **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user=self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user
class User(AbstractBaseUser,PermissionsMixin):
    """User in the system"""
    class Role(models.TextChoices):
        """Roles of Users."""
        AUTHOR = 'author', 'Author'
        PARTICIPANT = 'participant', 'Participant'

    email = models.EmailField(max_length=255,unique=True)
    name = models.CharField(max_length=255)

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        null = True,
        blank=True
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    affiliation = models.CharField(max_length=255, null=True)
    background_user = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=10, blank= True)
    objects = UserManager()

    USERNAME_FIELD = 'email'

class Event(models.Model):
    """Event object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    
    start_date = models.DateField()
    end_date = models.DateField()
    topics = models.ManyToManyField('Topic')

    def __str__(self):
        return self.title
    
class Topic(models.Model):
    """Topic object"""
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

def paper_pdf_file_path(instance, filename):
    """Generate fiel path for uploaded paper PDFs."""
    ext = os.path.splitext(filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    return os.path.join("uploads", "papers", filename)

class Paper(models.Model):
    """Object paper."""

    class PaperType(models.TextChoices):
        """Type of paper object."""
        ORAL = "oral", "Oral"
        POSTER = "poster", "Poster"
        WORKSHOP = "workshop", "Workshop"

    class Status(models.TextChoices):
        """Status of paper."""
        SUBMITTED = "submitted", "Submitted"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    title = models.CharField(max_length=255)
    abstract = models.TextField()
    keywords = models.CharField(max_length=255)
    paper_type = models.CharField(
        max_length=20,
        choices=PaperType.choices
    )
    pdf_file = models.FileField(null=True, upload_to=paper_pdf_file_path)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SUBMITTED
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields= ["event", "status"]),
            models.Index(fields=["author"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.author.email}"