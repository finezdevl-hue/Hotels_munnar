from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from hotels import views as hotel_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', hotel_views.home, name='home'),
    path('hotels/', include('hotels.urls')),
    path('bookings/', include('bookings.urls')),
    path('accounts/', include('accounts.urls')),
    path('panel/', include('custom_admin.urls')),
    path('staff/', include('employees.urls')),
]
