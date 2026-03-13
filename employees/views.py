from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

from hotels.models import Hotel, Room
from bookings.models import Booking
from hotels.models import Review
from .models import HotelEmployee


# ────────────────────────────────────────────────────────────────
#  DECORATORS / HELPERS
# ────────────────────────────────────────────────────────────────

def employee_required(view_func):
    """User must be logged in AND be an employee."""
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            emp = request.user.employee_profile
            if not emp.is_active:
                messages.error(request, "Your employee account has been deactivated.")
                return redirect('employee_login')
            request.employee = emp
            request.hotel    = emp.hotel
        except HotelEmployee.DoesNotExist:
            messages.error(request, "This area is for hotel employees only.")
            return redirect('employee_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def owner_required(view_func):
    """User must be a hotel owner (for managing employees)."""
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            if not request.user.profile.is_hotel_owner:
                messages.error(request, "Hotel owners only.")
                return redirect('home')
        except Exception:
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def require_perm(perm_name):
    """Employee must have a specific permission."""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            emp = getattr(request, 'employee', None)
            if emp and not getattr(emp, perm_name, False):
                messages.error(request, "You don't have permission for this action.")
                return redirect('employee_dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ────────────────────────────────────────────────────────────────
#  EMPLOYEE LOGIN / LOGOUT
# ────────────────────────────────────────────────────────────────

def employee_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            try:
                emp = user.employee_profile
                if not emp.is_active:
                    messages.error(request, "Your employee account has been deactivated by the hotel owner.")
                else:
                    login(request, user)
                    return redirect('employee_dashboard')
            except HotelEmployee.DoesNotExist:
                messages.error(request, "No employee account found. Please contact your hotel manager.")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'employees/login.html')


def employee_logout(request):
    logout(request)
    return redirect('employee_login')


# ────────────────────────────────────────────────────────────────
#  EMPLOYEE PORTAL VIEWS
# ────────────────────────────────────────────────────────────────

@employee_required
def employee_dashboard(request):
    hotel = request.hotel
    emp   = request.employee

    # stats the employee is allowed to see
    total_bookings    = Booking.objects.filter(room__hotel=hotel).count() if emp.can_view_bookings else None
    pending_bookings  = Booking.objects.filter(room__hotel=hotel, status='pending').count() if emp.can_view_bookings else None
    confirmed_bookings= Booking.objects.filter(room__hotel=hotel, status='confirmed').count() if emp.can_view_bookings else None
    total_rooms       = Room.objects.filter(hotel=hotel).count() if emp.can_view_rooms else None
    recent_bookings   = Booking.objects.filter(room__hotel=hotel).order_by('-created_at')[:6] if emp.can_view_bookings else []
    total_reviews     = hotel.reviews.count() if emp.can_view_reviews else None

    return render(request, 'employees/dashboard.html', {
        'hotel': hotel, 'emp': emp,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'total_rooms': total_rooms,
        'recent_bookings': recent_bookings,
        'total_reviews': total_reviews,
    })


@employee_required
def employee_bookings(request):
    emp   = request.employee
    hotel = request.hotel
    if not emp.can_view_bookings:
        messages.error(request, "You don't have permission to view bookings.")
        return redirect('employee_dashboard')

    bookings = Booking.objects.filter(room__hotel=hotel).select_related('room', 'user').order_by('-created_at')

    # filter
    status = request.GET.get('status', '')
    q      = request.GET.get('q', '')
    if status:
        bookings = bookings.filter(status=status)
    if q:
        bookings = bookings.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q) |
            Q(email__icontains=q) | Q(booking_ref__icontains=q)
        )

    paginator = Paginator(bookings, 15)
    return render(request, 'employees/bookings.html', {
        'hotel': hotel, 'emp': emp,
        'bookings': paginator.get_page(request.GET.get('page')),
        'current_status': status,
        'status_choices': Booking.STATUS_CHOICES,
    })


@employee_required
def employee_booking_detail(request, pk):
    emp   = request.employee
    hotel = request.hotel
    if not emp.can_view_bookings:
        return redirect('employee_dashboard')
    booking = get_object_or_404(Booking, pk=pk, room__hotel=hotel)

    if request.method == 'POST' and emp.can_manage_bookings:
        new_status = request.POST.get('status')
        if new_status in dict(Booking.STATUS_CHOICES):
            booking.status = new_status
            booking.save()
            messages.success(request, f"Booking status updated to {booking.get_status_display()}.")
        return redirect('employee_booking_detail', pk=pk)

    return render(request, 'employees/booking_detail.html', {
        'hotel': hotel, 'emp': emp, 'booking': booking,
        'status_choices': Booking.STATUS_CHOICES,
    })


@employee_required
def employee_rooms(request):
    emp   = request.employee
    hotel = request.hotel
    if not emp.can_view_rooms:
        messages.error(request, "You don't have permission to view rooms.")
        return redirect('employee_dashboard')
    rooms = Room.objects.filter(hotel=hotel).select_related('room_type')
    return render(request, 'employees/rooms.html', {
        'hotel': hotel, 'emp': emp, 'rooms': rooms,
    })


@employee_required
def employee_guests(request):
    emp   = request.employee
    hotel = request.hotel
    if not emp.can_view_guests:
        messages.error(request, "You don't have permission to view guests.")
        return redirect('employee_dashboard')

    # unique guests who booked this hotel
    guests = User.objects.filter(
        bookings__room__hotel=hotel
    ).distinct().select_related('profile')

    q = request.GET.get('q', '')
    if q:
        guests = guests.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q)
        )

    paginator = Paginator(guests, 20)
    return render(request, 'employees/guests.html', {
        'hotel': hotel, 'emp': emp,
        'guests': paginator.get_page(request.GET.get('page')),
    })


@employee_required
def employee_reviews(request):
    emp   = request.employee
    hotel = request.hotel
    if not emp.can_view_reviews:
        messages.error(request, "You don't have permission to view reviews.")
        return redirect('employee_dashboard')
    reviews = hotel.reviews.select_related('user').order_by('-created_at')
    return render(request, 'employees/reviews.html', {
        'hotel': hotel, 'emp': emp, 'reviews': reviews,
    })


@employee_required
def employee_review_delete(request, pk):
    emp   = request.employee
    hotel = request.hotel
    if not emp.can_manage_reviews:
        messages.error(request, "No permission.")
        return redirect('employee_reviews')
    review = get_object_or_404(Review, pk=pk, hotel=hotel)
    review.delete()
    messages.success(request, "Review deleted.")
    return redirect('employee_reviews')


@employee_required
def employee_profile(request):
    emp  = request.employee
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name  = request.POST.get('last_name',  user.last_name)
        user.email      = request.POST.get('email',      user.email)
        new_pw = request.POST.get('new_password', '')
        if new_pw:
            user.set_password(new_pw)
        user.save()
        messages.success(request, "Profile updated.")
        return redirect('employee_profile')
    return render(request, 'employees/profile.html', {
        'hotel': request.hotel, 'emp': emp,
    })


# ────────────────────────────────────────────────────────────────
#  OWNER — EMPLOYEE MANAGEMENT
# ────────────────────────────────────────────────────────────────

@owner_required
def manage_employees(request, slug):
    hotel = get_object_or_404(Hotel, slug=slug, owner=request.user)
    employees = HotelEmployee.objects.filter(hotel=hotel).select_related('user')
    return render(request, 'employees/manage_employees.html', {
        'hotel': hotel,
        'employees': employees,
    })


@owner_required
def add_employee(request, slug):
    hotel = get_object_or_404(Hotel, slug=slug, owner=request.user)
    if request.method == 'POST':
        username   = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip()
        password   = request.POST.get('password', '')
        job_title  = request.POST.get('job_title', 'Staff').strip()

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, 'employees/add_employee.html', {'hotel': hotel})

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' is already taken.")
            return render(request, 'employees/add_employee.html', {'hotel': hotel, 'post': request.POST})

        user = User.objects.create_user(
            username=username, email=email,
            password=password,
            first_name=first_name, last_name=last_name,
        )

        emp = HotelEmployee.objects.create(
            user=user, hotel=hotel, created_by=request.user,
            job_title=job_title,
            can_view_bookings   = 'perm_view_bookings'   in request.POST,
            can_manage_bookings = 'perm_manage_bookings' in request.POST,
            can_view_rooms      = 'perm_view_rooms'      in request.POST,
            can_manage_rooms    = 'perm_manage_rooms'    in request.POST,
            can_view_guests     = 'perm_view_guests'     in request.POST,
            can_view_reviews    = 'perm_view_reviews'    in request.POST,
            can_manage_reviews  = 'perm_manage_reviews'  in request.POST,
            can_edit_hotel_info = 'perm_edit_hotel'      in request.POST,
            can_manage_employees= 'perm_manage_employees'in request.POST,
        )

        messages.success(request, f"Employee '{username}' created successfully.")
        return redirect('manage_employees', slug=slug)

    return render(request, 'employees/add_employee.html', {'hotel': hotel})


@owner_required
def edit_employee(request, slug, emp_id):
    hotel = get_object_or_404(Hotel, slug=slug, owner=request.user)
    emp   = get_object_or_404(HotelEmployee, pk=emp_id, hotel=hotel)

    if request.method == 'POST':
        emp.job_title           = request.POST.get('job_title', emp.job_title)
        emp.is_active           = 'is_active'            in request.POST
        emp.can_view_bookings   = 'perm_view_bookings'   in request.POST
        emp.can_manage_bookings = 'perm_manage_bookings' in request.POST
        emp.can_view_rooms      = 'perm_view_rooms'      in request.POST
        emp.can_manage_rooms    = 'perm_manage_rooms'    in request.POST
        emp.can_view_guests     = 'perm_view_guests'     in request.POST
        emp.can_view_reviews    = 'perm_view_reviews'    in request.POST
        emp.can_manage_reviews  = 'perm_manage_reviews'  in request.POST
        emp.can_edit_hotel_info = 'perm_edit_hotel'      in request.POST
        emp.can_manage_employees= 'perm_manage_employees'in request.POST
        emp.save()

        # also allow resetting password
        new_pw = request.POST.get('new_password', '').strip()
        if new_pw:
            emp.user.set_password(new_pw)
            emp.user.save()
            messages.success(request, "Password updated.")

        # update name/email
        emp.user.first_name = request.POST.get('first_name', emp.user.first_name)
        emp.user.last_name  = request.POST.get('last_name',  emp.user.last_name)
        emp.user.email      = request.POST.get('email',      emp.user.email)
        emp.user.save()

        messages.success(request, f"Employee '{emp.user.username}' updated.")
        return redirect('manage_employees', slug=slug)

    return render(request, 'employees/edit_employee.html', {
        'hotel': hotel, 'emp': emp,
    })


@owner_required
def delete_employee(request, slug, emp_id):
    hotel = get_object_or_404(Hotel, slug=slug, owner=request.user)
    emp   = get_object_or_404(HotelEmployee, pk=emp_id, hotel=hotel)
    user  = emp.user
    user.delete()   # cascades to HotelEmployee
    messages.success(request, "Employee removed.")
    return redirect('manage_employees', slug=slug)


@owner_required
def toggle_employee(request, slug, emp_id):
    hotel = get_object_or_404(Hotel, slug=slug, owner=request.user)
    emp   = get_object_or_404(HotelEmployee, pk=emp_id, hotel=hotel)
    emp.is_active = not emp.is_active
    emp.save()
    messages.success(request, f"Employee {'activated' if emp.is_active else 'deactivated'}.")
    return redirect('manage_employees', slug=slug)
