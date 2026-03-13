from django.contrib import admin
from django.utils import timezone
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'owner_approval_status', 'phone', 'country', 'owner_requested_at']
    list_filter  = ['role', 'owner_approval_status', 'country']
    search_fields = ['user__username', 'user__email']
    list_editable = ['owner_approval_status']
    readonly_fields = ['owner_requested_at', 'owner_reviewed_at']
    actions = ['approve_owners', 'reject_owners']

    def approve_owners(self, request, queryset):
        queryset.filter(role='hotel_owner').update(
            owner_approval_status='approved',
            owner_reviewed_at=timezone.now()
        )
        self.message_user(request, 'Selected owners approved.')
    approve_owners.short_description = 'Approve selected hotel owners'

    def reject_owners(self, request, queryset):
        queryset.filter(role='hotel_owner').update(
            owner_approval_status='rejected',
            owner_reviewed_at=timezone.now()
        )
        self.message_user(request, 'Selected owners rejected.')
    reject_owners.short_description = 'Reject selected hotel owners'
