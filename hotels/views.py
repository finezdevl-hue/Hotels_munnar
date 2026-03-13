from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from .models import Hotel, HotelImage, Room, Review, Amenity
from .forms import HotelForm, HotelImageForm, RoomForm, ReviewForm, HotelSearchForm


def home(request):
    featured_hotels = Hotel.objects.filter(is_active=True, is_featured=True)[:6]
    all_hotels = Hotel.objects.filter(is_active=True)[:8]
    search_form = HotelSearchForm()
    context = {
        'featured_hotels': featured_hotels,
        'all_hotels': all_hotels,
        'search_form': search_form,
        'total_hotels': Hotel.objects.filter(is_active=True).count(),
    }
    return render(request, 'home.html', context)


def hotel_list(request):
    hotels = Hotel.objects.filter(is_active=True)
    form = HotelSearchForm(request.GET)

    if form.is_valid():
        city = form.cleaned_data.get('city')
        stars = form.cleaned_data.get('stars')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        query = form.cleaned_data.get('query')

        if city:
            hotels = hotels.filter(city__icontains=city)
        if stars:
            hotels = hotels.filter(stars=stars)
        if query:
            hotels = hotels.filter(
                Q(name__icontains=query) |
                Q(city__icontains=query) |
                Q(description__icontains=query)
            )
        if min_price:
            hotels = hotels.filter(rooms__price_per_night__gte=min_price).distinct()
        if max_price:
            hotels = hotels.filter(rooms__price_per_night__lte=max_price).distinct()

    paginator = Paginator(hotels, 9)
    page = request.GET.get('page')
    hotels_page = paginator.get_page(page)

    return render(request, 'hotels/hotel_list.html', {
        'hotels': hotels_page,
        'form': form,
        'total': paginator.count,
    })


def hotel_detail(request, slug):
    hotel = get_object_or_404(Hotel, slug=slug, is_active=True)
    rooms = hotel.rooms.filter(is_available=True)
    images = hotel.images.all()
    reviews = hotel.reviews.all()[:10]
    avg_rating = hotel.get_average_rating()

    review_form = ReviewForm()
    can_review = False
    if request.user.is_authenticated:
        can_review = not hotel.reviews.filter(user=request.user).exists()

    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.hotel = hotel
            review.user = request.user
            review.save()
            messages.success(request, 'Your review has been submitted!')
            return redirect('hotel_detail', slug=slug)

    return render(request, 'hotels/hotel_detail.html', {
        'hotel': hotel,
        'rooms': rooms,
        'images': images,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_form': review_form,
        'can_review': can_review,
    })


def _require_approved_owner(request):
    """Returns None if OK, or a redirect response if not approved."""
    profile = request.user.profile
    if profile.is_hotel_owner:
        return None
    if profile.owner_approval_status == 'pending':
        return redirect('approval_pending')
    messages.error(request, 'You need to be an approved hotel owner to do that.')
    return redirect('home')


@login_required
def hotel_dashboard(request):
    """Hotel owner dashboard"""
    block = _require_approved_owner(request)
    if block:
        return block
    hotels = Hotel.objects.filter(owner=request.user)
    return render(request, 'hotels/dashboard.html', {'hotels': hotels})


@login_required
def hotel_create(request):
    block = _require_approved_owner(request)
    if block:
        return block
    if request.method == 'POST':
        form = HotelForm(request.POST)
        if form.is_valid():
            hotel = form.save(commit=False)
            hotel.owner = request.user
            hotel.save()
            form.save_m2m()
            messages.success(request, f'Hotel "{hotel.name}" created successfully!')
            return redirect('hotel_manage', slug=hotel.slug)
    else:
        form = HotelForm()
    return render(request, 'hotels/hotel_form.html', {'form': form, 'title': 'Add New Hotel'})


@login_required
def hotel_edit(request, slug):
    hotel = get_object_or_404(Hotel, slug=slug, owner=request.user)
    if request.method == 'POST':
        form = HotelForm(request.POST, instance=hotel)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hotel updated successfully!')
            return redirect('hotel_manage', slug=hotel.slug)
    else:
        form = HotelForm(instance=hotel)
    return render(request, 'hotels/hotel_form.html', {'form': form, 'hotel': hotel, 'title': 'Edit Hotel'})


@login_required
def hotel_manage(request, slug):
    hotel = get_object_or_404(Hotel, slug=slug, owner=request.user)
    rooms = hotel.rooms.all()
    images = hotel.images.all()
    from bookings.models import Booking
    bookings = Booking.objects.filter(room__hotel=hotel).order_by('-created_at')[:10]
    return render(request, 'hotels/hotel_manage.html', {
        'hotel': hotel,
        'rooms': rooms,
        'images': images,
        'bookings': bookings,
    })


@login_required
def upload_hotel_image(request, slug):
    hotel = get_object_or_404(Hotel, slug=slug, owner=request.user)
    if request.method == 'POST':
        form = HotelImageForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.save(commit=False)
            img.hotel = hotel
            img.save()
            messages.success(request, 'Image uploaded successfully!')
        return redirect('hotel_manage', slug=slug)
    return redirect('hotel_manage', slug=slug)


@login_required
def delete_hotel_image(request, image_id):
    image = get_object_or_404(HotelImage, id=image_id, hotel__owner=request.user)
    slug = image.hotel.slug
    image.image.delete()
    image.delete()
    messages.success(request, 'Image deleted.')
    return redirect('hotel_manage', slug=slug)


@login_required
def set_main_image(request, image_id):
    image = get_object_or_404(HotelImage, id=image_id, hotel__owner=request.user)
    image.is_main = True
    image.save()
    messages.success(request, 'Main image updated.')
    return redirect('hotel_manage', slug=image.hotel.slug)


@login_required
def room_create(request, slug):
    hotel = get_object_or_404(Hotel, slug=slug, owner=request.user)
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save(commit=False)
            room.hotel = hotel
            room.save()
            form.save_m2m()
            messages.success(request, f'Room "{room.name}" added!')
            return redirect('hotel_manage', slug=slug)
    else:
        form = RoomForm()
    return render(request, 'hotels/room_form.html', {'form': form, 'hotel': hotel})


@login_required
def room_edit(request, room_id):
    room = get_object_or_404(Room, id=room_id, hotel__owner=request.user)
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room updated!')
            return redirect('hotel_manage', slug=room.hotel.slug)
    else:
        form = RoomForm(instance=room)
    return render(request, 'hotels/room_form.html', {'form': form, 'hotel': room.hotel, 'room': room})


@login_required
def room_delete(request, room_id):
    room = get_object_or_404(Room, id=room_id, hotel__owner=request.user)
    slug = room.hotel.slug
    room.delete()
    messages.success(request, 'Room deleted.')
    return redirect('hotel_manage', slug=slug)
