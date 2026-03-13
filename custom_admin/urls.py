from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),
    path('hotels/', views.hotels_list, name='admin_hotels'),
    path('hotels/create/', views.hotel_create, name='admin_hotel_create'),
    path('hotels/<slug:slug>/edit/', views.hotel_edit, name='admin_hotel_edit'),
    path('hotels/<slug:slug>/toggle/', views.hotel_toggle, name='admin_hotel_toggle'),
    path('bookings/', views.bookings_list, name='admin_bookings'),
    path('bookings/<int:pk>/status/', views.booking_update_status, name='admin_booking_status'),
    path('bookings/<int:pk>/payment/', views.booking_update_payment, name='admin_booking_payment'),
    path('users/', views.users_list, name='admin_users'),
    path('users/<int:pk>/', views.user_detail, name='admin_user_detail'),
    path('users/<int:pk>/toggle-staff/', views.toggle_staff, name='admin_toggle_staff'),
    path('reviews/', views.reviews_list, name='admin_reviews'),
    path('reviews/<int:pk>/delete/', views.review_delete, name='admin_review_delete'),
    path('amenities/', views.amenities_view, name='admin_amenities'),
    path('amenities/create/', views.amenity_create, name='admin_amenity_create'),
    path('amenities/<int:pk>/delete/', views.amenity_delete, name='admin_amenity_delete'),
    path('room-types/', views.room_types_view, name='admin_room_types'),
    path('room-types/create/', views.room_type_create, name='admin_room_type_create'),
    path('room-types/<int:pk>/delete/', views.room_type_delete, name='admin_room_type_delete'),
]
