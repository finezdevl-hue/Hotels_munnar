from django.db import models
from django.contrib.auth.models import User
from hotels.models import Hotel


class HotelEmployee(models.Model):
    """An employee account linked to a hotel owner."""
    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    hotel       = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='employees')
    created_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_employees')
    job_title   = models.CharField(max_length=100, default='Staff')
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    # ── Granular permissions ────────────────────────────────────
    can_view_bookings    = models.BooleanField(default=True)
    can_manage_bookings  = models.BooleanField(default=False)   # update status
    can_view_rooms       = models.BooleanField(default=True)
    can_manage_rooms     = models.BooleanField(default=False)   # add / edit rooms
    can_view_guests      = models.BooleanField(default=True)
    can_view_reviews     = models.BooleanField(default=True)
    can_manage_reviews   = models.BooleanField(default=False)   # delete reviews
    can_edit_hotel_info  = models.BooleanField(default=False)   # hotel details / images
    can_manage_employees = models.BooleanField(default=False)   # add / edit other staff

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} @ {self.hotel.name}"

    def has_perm(self, perm):
        return getattr(self, perm, False)

    @property
    def permission_summary(self):
        perms = []
        if self.can_view_bookings:   perms.append('View Bookings')
        if self.can_manage_bookings: perms.append('Manage Bookings')
        if self.can_view_rooms:      perms.append('View Rooms')
        if self.can_manage_rooms:    perms.append('Manage Rooms')
        if self.can_view_guests:     perms.append('View Guests')
        if self.can_view_reviews:    perms.append('View Reviews')
        if self.can_manage_reviews:  perms.append('Manage Reviews')
        if self.can_edit_hotel_info: perms.append('Edit Hotel Info')
        if self.can_manage_employees:perms.append('Manage Employees')
        return perms
