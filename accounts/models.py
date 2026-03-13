from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('hotel_owner', 'Hotel Owner'),
    ]
    APPROVAL_CHOICES = [
        ('not_requested', 'Not Requested'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='guest')
    owner_approval_status = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default='not_requested')
    owner_rejection_reason = models.TextField(blank=True)
    owner_requested_at = models.DateTimeField(null=True, blank=True)
    owner_reviewed_at = models.DateTimeField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    passport_number = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"

    @property
    def is_hotel_owner(self):
        return self.role == 'hotel_owner' and self.owner_approval_status == 'approved'

    @property
    def is_pending_approval(self):
        return self.owner_approval_status == 'pending'


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
