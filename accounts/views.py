from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .forms import RegisterForm, ProfileForm, LoginForm
from .models import UserProfile


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data.get('role', 'guest')
            if role == 'hotel_owner':
                user.profile.role = 'hotel_owner'
                user.profile.owner_approval_status = 'pending'
                user.profile.owner_requested_at = timezone.now()
                user.profile.save()
                login(request, user)
                messages.info(request,
                    'Your hotel owner application has been submitted and is awaiting admin approval. '
                    'You will be notified once approved.')
                return redirect('approval_pending')
            else:
                user.profile.role = 'guest'
                user.profile.save()
                login(request, user)
                messages.success(request, f'Welcome, {user.first_name or user.username}!')
                return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm(request)
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def approval_pending_view(request):
    """Shown to hotel owners who are awaiting admin approval."""
    profile = request.user.profile
    if profile.owner_approval_status == 'approved':
        return redirect('hotel_dashboard')
    if profile.owner_approval_status not in ('pending', 'rejected'):
        return redirect('home')
    return render(request, 'accounts/approval_pending.html', {'profile': profile})


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user.profile, user=request.user)

    from bookings.models import Booking
    recent_bookings = Booking.objects.filter(user=request.user)[:5]

    return render(request, 'accounts/profile.html', {
        'form': form,
        'recent_bookings': recent_bookings,
    })


# ── Admin-only views ──────────────────────────────────────────────────────────

def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def owner_approval_list(request):
    """Admin view: list all hotel owner applications."""
    pending   = UserProfile.objects.filter(role='hotel_owner', owner_approval_status='pending').select_related('user')
    approved  = UserProfile.objects.filter(role='hotel_owner', owner_approval_status='approved').select_related('user')
    rejected  = UserProfile.objects.filter(role='hotel_owner', owner_approval_status='rejected').select_related('user')
    return render(request, 'accounts/owner_approval_list.html', {
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
    })


@login_required
@user_passes_test(is_staff)
def approve_owner(request, profile_id):
    profile = get_object_or_404(UserProfile, id=profile_id, role='hotel_owner')
    profile.owner_approval_status = 'approved'
    profile.owner_rejection_reason = ''
    profile.owner_reviewed_at = timezone.now()
    profile.save()
    messages.success(request, f'{profile.user.username} has been approved as a hotel owner.')
    return redirect('owner_approval_list')


@login_required
@user_passes_test(is_staff)
def reject_owner(request, profile_id):
    profile = get_object_or_404(UserProfile, id=profile_id, role='hotel_owner')
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        profile.owner_approval_status = 'rejected'
        profile.owner_rejection_reason = reason
        profile.owner_reviewed_at = timezone.now()
        profile.save()
        messages.warning(request, f'{profile.user.username} has been rejected.')
        return redirect('owner_approval_list')
    return render(request, 'accounts/reject_owner.html', {'profile': profile})
