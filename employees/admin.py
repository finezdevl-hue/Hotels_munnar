from django.contrib import admin
from .models import HotelEmployee

@admin.register(HotelEmployee)
class HotelEmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'hotel', 'job_title', 'is_active', 'created_at']
    list_filter  = ['is_active', 'hotel']
    search_fields = ['user__username', 'hotel__name']
