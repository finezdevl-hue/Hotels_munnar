from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


class Amenity(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='bi-check-circle')  # Bootstrap icon class

    class Meta:
        verbose_name_plural = 'Amenities'

    def __str__(self):
        return self.name


class Hotel(models.Model):
    STAR_CHOICES = [(i, f'{i} Star') for i in range(1, 6)]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hotels')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    stars = models.IntegerField(choices=STAR_CHOICES, default=3)
    amenities = models.ManyToManyField(Amenity, blank=True)
    check_in_time = models.TimeField(default='14:00')
    check_out_time = models.TimeField(default='11:00')
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_main_image(self):
        img = self.images.filter(is_main=True).first()
        return img if img else self.images.first()

    def get_average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return None

    def get_min_price(self):
        rooms = self.rooms.filter(is_available=True)
        if rooms.exists():
            return rooms.order_by('price_per_night').first().price_per_night
        return None


class HotelImage(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='hotels/images/')
    caption = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'uploaded_at']

    def __str__(self):
        return f"{self.hotel.name} - Image {self.id}"

    def save(self, *args, **kwargs):
        if self.is_main:
            # Ensure only one main image per hotel
            HotelImage.objects.filter(hotel=self.hotel, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)


class RoomType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_type = models.ForeignKey(RoomType, on_delete=models.SET_NULL, null=True)
    room_number = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    description = models.TextField()
    capacity = models.PositiveIntegerField(default=2)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    size_sqm = models.PositiveIntegerField(null=True, blank=True)
    amenities = models.ManyToManyField(Amenity, blank=True)
    image = models.ImageField(upload_to='rooms/images/', null=True, blank=True)
    is_available = models.BooleanField(default=True)
    bed_type = models.CharField(max_length=100, default='Double Bed')

    class Meta:
        unique_together = ['hotel', 'room_number']

    def __str__(self):
        return f"{self.hotel.name} - {self.name} ({self.room_number})"


class Review(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    cleanliness = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=5)
    service = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=5)
    location = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=5)
    value = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['hotel', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.hotel.name} ({self.rating}/5)"
