from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta, date

from hotels.models import Hotel, Room, Review, Amenity, RoomType
from hotels.forms import HotelForm
from bookings.models import Booking
from accounts.models import UserProfile


def staff_required(view_func):
    decorated = login_required(user_passes_test(lambda u: u.is_staff)(view_func))
    return decorated


def get_booking_chart_data():
    """Last 7 days booking counts."""
    labels, data = [], []
    for i in range(6, -1, -1):
        day = date.today() - timedelta(days=i)
        count = Booking.objects.filter(created_at__date=day).count()
        labels.append(day.strftime('%d %b'))
        data.append(count)
    return labels, data


@staff_required
def dashboard(request):
    total_hotels    = Hotel.objects.count()
    active_hotels   = Hotel.objects.filter(is_active=True).count()
    total_bookings  = Booking.objects.count()
    confirmed_bookings = Booking.objects.filter(status='confirmed').count()
    pending_bookings   = Booking.objects.filter(status='pending').count()
    total_users     = User.objects.count()
    hotel_owners    = UserProfile.objects.filter(role='hotel_owner', owner_approval_status='approved').count()
    total_reviews   = Review.objects.count()
    total_revenue   = Booking.objects.filter(
        status__in=['confirmed', 'checked_in', 'checked_out']
    ).aggregate(total=Sum('total_price'))['total'] or 0

    recent_bookings = Booking.objects.select_related('room__hotel', 'user').order_by('-created_at')[:8]
    top_hotels      = Hotel.objects.annotate(booking_count=Count('rooms__bookings')).order_by('-booking_count')[:5]
    pending_owner_requests = UserProfile.objects.filter(
        role='hotel_owner', owner_approval_status='pending'
    ).select_related('user')[:5]

    booking_labels, booking_data = get_booking_chart_data()

    status_data = [
        Booking.objects.filter(status='confirmed').count(),
        Booking.objects.filter(status='pending').count(),
        Booking.objects.filter(status='cancelled').count(),
        Booking.objects.filter(status='checked_in').count(),
        Booking.objects.filter(status='checked_out').count(),
    ]

    return render(request, 'custom_admin/dashboard.html', {
        'total_hotels': total_hotels,
        'active_hotels': active_hotels,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'pending_bookings': pending_bookings,
        'total_users': total_users,
        'hotel_owners': hotel_owners,
        'total_reviews': total_reviews,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'top_hotels': top_hotels,
        'pending_owner_requests': pending_owner_requests,
        'booking_labels': booking_labels,
        'booking_data': booking_data,
        'status_data': status_data,
    })


@staff_required
def hotels_list(request):
    hotels = Hotel.objects.annotate(booking_count=Count('rooms__bookings')).select_related('owner')
    q      = request.GET.get('q', '')
    stars  = request.GET.get('stars', '')
    status = request.GET.get('status', '')

    if q:
        hotels = hotels.filter(Q(name__icontains=q) | Q(city__icontains=q) | Q(country__icontains=q))
    if stars:
        hotels = hotels.filter(stars=stars)
    if status == 'active':
        hotels = hotels.filter(is_active=True)
    elif status == 'inactive':
        hotels = hotels.filter(is_active=False)
    elif status == 'featured':
        hotels = hotels.filter(is_featured=True)

    paginator = Paginator(hotels.order_by('-created_at'), 15)
    return render(request, 'custom_admin/hotels.html', {
        'hotels': paginator.get_page(request.GET.get('page')),
    })


@staff_required
def hotel_create(request):
    all_users    = User.objects.filter(is_active=True)
    all_amenities = Amenity.objects.all()
    if request.method == 'POST':
        form = HotelForm(request.POST)
        if form.is_valid():
            hotel = form.save(commit=False)
            owner_id = request.POST.get('owner')
            if owner_id:
                hotel.owner = get_object_or_404(User, pk=owner_id)
            else:
                hotel.owner = request.user
            hotel.save()
            form.save_m2m()
            messages.success(request, f'Hotel "{hotel.name}" created!')
            return redirect('admin_hotels')
    else:
        form = HotelForm()
    return render(request, 'custom_admin/hotel_form.html', {
        'form': form,
        'all_users': all_users,
        'all_amenities': all_amenities,
        'selected_amenities': [],
    })


@staff_required
def hotel_edit(request, slug):
    hotel        = get_object_or_404(Hotel, slug=slug)
    all_users    = User.objects.filter(is_active=True)
    all_amenities = Amenity.objects.all()
    selected_amenities = list(hotel.amenities.values_list('pk', flat=True))

    if request.method == 'POST':
        form = HotelForm(request.POST, instance=hotel)
        if form.is_valid():
            h = form.save(commit=False)
            owner_id = request.POST.get('owner')
            if owner_id:
                h.owner = get_object_or_404(User, pk=owner_id)
            h.save()
            form.save_m2m()
            messages.success(request, 'Hotel updated!')
            return redirect('admin_hotels')
    else:
        form = HotelForm(instance=hotel)
    return render(request, 'custom_admin/hotel_form.html', {
        'form': form,
        'hotel': hotel,
        'all_users': all_users,
        'all_amenities': all_amenities,
        'selected_amenities': selected_amenities,
    })


@staff_required
def hotel_toggle(request, slug):
    hotel = get_object_or_404(Hotel, slug=slug)
    hotel.is_active = not hotel.is_active
    hotel.save()
    messages.success(request, f'{"Activated" if hotel.is_active else "Deactivated"}: {hotel.name}')
    return redirect('admin_hotels')


@staff_required
def bookings_list(request):
    bookings = Booking.objects.select_related('room__hotel', 'user').order_by('-created_at')
    current_status = request.GET.get('status', '')
    q = request.GET.get('q', '')
    hotel_id = request.GET.get('hotel', '')
    date_from = request.GET.get('date_from', '')

    if current_status:
        bookings = bookings.filter(status=current_status)
    if q:
        bookings = bookings.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q) |
            Q(email__icontains=q) | Q(booking_ref__icontains=q)
        )
    if hotel_id:
        bookings = bookings.filter(room__hotel_id=hotel_id)
    if date_from:
        bookings = bookings.filter(check_in__gte=date_from)

    total_revenue = bookings.filter(
        status__in=['confirmed', 'checked_in', 'checked_out']
    ).aggregate(total=Sum('total_price'))['total'] or 0

    paginator = Paginator(bookings, 20)

    import urllib.parse
    params = request.GET.copy()
    params.pop('page', None)
    query_params = params.urlencode()

    status_tabs = [
        ('All', '', '#6B7280'),
        ('Pending', 'pending', '#F59E0B'),
        ('Confirmed', 'confirmed', '#10B981'),
        ('Checked In', 'checked_in', '#3B82F6'),
        ('Checked Out', 'checked_out', '#6B7280'),
        ('Cancelled', 'cancelled', '#EF4444'),
    ]

    return render(request, 'custom_admin/bookings.html', {
        'bookings': paginator.get_page(request.GET.get('page')),
        'current_status': current_status,
        'total_revenue': total_revenue,
        'all_hotels': Hotel.objects.all(),
        'query_params': query_params,
        'status_tabs': status_tabs,
        'booking_statuses': Booking.STATUS_CHOICES,
    })


@staff_required
def booking_update_status(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Booking.STATUS_CHOICES):
            booking.status = new_status
            booking.save()
    return redirect(request.META.get('HTTP_REFERER', 'admin_bookings'))


@staff_required
def booking_update_payment(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        ps = request.POST.get('payment_status')
        if ps in ['unpaid', 'paid', 'refunded']:
            booking.payment_status = ps
            booking.save()
    return redirect(request.META.get('HTTP_REFERER', 'admin_bookings'))


@staff_required
def users_list(request):
    users = User.objects.select_related('profile').annotate(
        booking_count=Count('bookings'),
        hotel_count=Count('hotels'),
    )
    q    = request.GET.get('q', '')
    role = request.GET.get('role', '')

    if q:
        users = users.filter(Q(username__icontains=q) | Q(email__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q))
    if role == 'guest':
        users = users.filter(profile__role='guest')
    elif role == 'hotel_owner':
        users = users.filter(profile__role='hotel_owner')
    elif role == 'staff':
        users = users.filter(is_staff=True)

    paginator = Paginator(users.order_by('-date_joined'), 20)
    return render(request, 'custom_admin/users.html', {
        'users': paginator.get_page(request.GET.get('page')),
    })


@staff_required
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    bookings = Booking.objects.filter(user=user).order_by('-created_at')
    hotels   = Hotel.objects.filter(owner=user)
    return render(request, 'custom_admin/user_detail.html', {
        'profile_user': user,
        'bookings': bookings,
        'hotels': hotels,
    })


@staff_required
def toggle_staff(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, "You can't change your own admin status.")
    else:
        user.is_staff = not user.is_staff
        user.is_superuser = user.is_staff
        user.save()
        messages.success(request, f'{"Granted" if user.is_staff else "Revoked"} admin access for {user.username}.')
    return redirect('admin_users')


@staff_required
def reviews_list(request):
    reviews = Review.objects.select_related('hotel', 'user').order_by('-created_at')
    paginator = Paginator(reviews, 20)
    return render(request, 'custom_admin/reviews.html', {
        'reviews': paginator.get_page(request.GET.get('page')),
    })


@staff_required
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.delete()
    messages.success(request, 'Review deleted.')
    return redirect('admin_reviews')


@staff_required
def amenities_view(request):
    return render(request, 'custom_admin/amenities.html', {
        'amenities': Amenity.objects.all(),
        'room_types': RoomType.objects.all(),
    })


@staff_required
def amenity_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        icon = request.POST.get('icon', 'bi-check-circle').strip()
        if name:
            Amenity.objects.get_or_create(name=name, defaults={'icon': icon})
            messages.success(request, f'Amenity "{name}" added.')
    return redirect('admin_amenities')


@staff_required
def amenity_delete(request, pk):
    amenity = get_object_or_404(Amenity, pk=pk)
    amenity.delete()
    messages.success(request, 'Amenity deleted.')
    return redirect('admin_amenities')


@staff_required
def room_type_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            RoomType.objects.get_or_create(name=name)
            messages.success(request, f'Room type "{name}" added.')
    return redirect('admin_amenities')


@staff_required
def room_type_delete(request, pk):
    rt = get_object_or_404(RoomType, pk=pk)
    rt.delete()
    messages.success(request, 'Room type deleted.')
    return redirect('admin_amenities')


@staff_required
def room_types_view(request):
    return redirect('admin_amenities')
