from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_ref_short', 'user', 'room', 'check_in', 'check_out', 'status', 'payment_status', 'total_price', 'created_at']
    list_filter = ['status', 'payment_status', 'check_in']
    search_fields = ['booking_ref', 'user__username', 'email', 'first_name', 'last_name']
    list_editable = ['status', 'payment_status']
    readonly_fields = ['booking_ref', 'created_at', 'updated_at']
