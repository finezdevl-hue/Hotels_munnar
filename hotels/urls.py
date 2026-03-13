from django.urls import path
from . import views

urlpatterns = [
    path('', views.hotel_list, name='hotel_list'),
    path('dashboard/', views.hotel_dashboard, name='hotel_dashboard'),
    path('create/', views.hotel_create, name='hotel_create'),
    path('<slug:slug>/', views.hotel_detail, name='hotel_detail'),
    path('<slug:slug>/edit/', views.hotel_edit, name='hotel_edit'),
    path('<slug:slug>/manage/', views.hotel_manage, name='hotel_manage'),
    path('<slug:slug>/upload-image/', views.upload_hotel_image, name='upload_hotel_image'),
    path('<slug:slug>/rooms/add/', views.room_create, name='room_create'),
    path('images/<int:image_id>/delete/', views.delete_hotel_image, name='delete_hotel_image'),
    path('images/<int:image_id>/set-main/', views.set_main_image, name='set_main_image'),
    path('rooms/<int:room_id>/edit/', views.room_edit, name='room_edit'),
    path('rooms/<int:room_id>/delete/', views.room_delete, name='room_delete'),
]
