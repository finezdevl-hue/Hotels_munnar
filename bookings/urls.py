from django.urls import path
from . import views

urlpatterns = [
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('book/<int:room_id>/', views.book_room, name='book_room'),
    path('<int:pk>/', views.booking_detail, name='booking_detail'),
    path('<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('<int:pk>/update-status/', views.update_booking_status, name='update_booking_status'),
    path('hotel/<slug:slug>/', views.hotel_bookings, name='hotel_bookings'),
]
