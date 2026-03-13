from django.contrib import admin
from .models import Hotel, HotelImage, Room, RoomType, Review, Amenity


class HotelImageInline(admin.TabularInline):
    model = HotelImage
    extra = 1


class RoomInline(admin.TabularInline):
    model = Room
    extra = 0


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'country', 'stars', 'owner', 'is_active', 'is_featured']
    list_filter = ['stars', 'is_active', 'is_featured', 'country']
    search_fields = ['name', 'city', 'country']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [HotelImageInline, RoomInline]
    list_editable = ['is_active', 'is_featured']


@admin.register(HotelImage)
class HotelImageAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'caption', 'is_main', 'order']
    list_filter = ['is_main']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'room_number', 'name', 'room_type', 'capacity', 'price_per_night', 'is_available']
    list_filter = ['is_available', 'room_type']
    list_editable = ['is_available', 'price_per_night']


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'user', 'rating', 'title', 'created_at']
    list_filter = ['rating']


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
