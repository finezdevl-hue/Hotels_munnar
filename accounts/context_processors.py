from .models import UserProfile


def pending_approvals(request):
    count = 0
    if request.user.is_authenticated and request.user.is_staff:
        count = UserProfile.objects.filter(role='hotel_owner', owner_approval_status='pending').count()
    return {'pending_approvals_count': count}
