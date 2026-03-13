from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from datetime import date
from .models import Booking
from .forms import BookingForm
from hotels.models import Room


@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id, is_available=True)
    hotel = room.hotel

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            check_in = form.cleaned_data['check_in']
            check_out = form.cleaned_data['check_out']

            # Check if room is already booked for those dates
            conflict = Booking.objects.filter(
                room=room,
                status__in=['pending', 'confirmed', 'checked_in'],
            ).filter(
                Q(check_in__lt=check_out) & Q(check_out__gt=check_in)
            ).exists()

            if conflict:
                messages.error(request, 'This room is not available for the selected dates.')
            elif check_in >= check_out:
                messages.error(request, 'Check-out must be after check-in.')
            elif check_in < date.today():
                messages.error(request, 'Check-in cannot be in the past.')
            else:
                booking = form.save(commit=False)
                booking.user = request.user
                booking.room = room
                nights = (check_out - check_in).days
                booking.total_price = room.price_per_night * nights
                booking.save()
                messages.success(request, f'Booking confirmed! Reference: {booking.booking_ref_short}')
                return redirect('booking_detail', pk=booking.pk)
    else:
        # Pre-fill user info
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        form = BookingForm(initial=initial)

    return render(request, 'bookings/book_room.html', {
        'form': form,
        'room': room,
        'hotel': hotel,
    })


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related('room__hotel')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})


@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.status in ['pending', 'confirmed']:
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled successfully.')
    else:
        messages.error(request, 'This booking cannot be cancelled.')
    return redirect('my_bookings')


@login_required
def hotel_bookings(request, slug):
    """For hotel owners to see their hotel's bookings"""
    from hotels.models import Hotel
    hotel = get_object_or_404(Hotel, slug=slug, owner=request.user)
    bookings = Booking.objects.filter(room__hotel=hotel).select_related('user', 'room')

    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    return render(request, 'bookings/hotel_bookings.html', {
        'hotel': hotel,
        'bookings': bookings,
        'status_filter': status_filter,
    })


@login_required
def update_booking_status(request, pk):
    """Hotel owners can update booking status"""
    booking = get_object_or_404(Booking, pk=pk, room__hotel__owner=request.user)
    new_status = request.POST.get('status')
    if new_status in ['confirmed', 'checked_in', 'checked_out', 'cancelled']:
        booking.status = new_status
        booking.save()
        messages.success(request, f'Booking status updated to {new_status}.')
    return redirect('hotel_bookings', slug=booking.room.hotel.slug)
