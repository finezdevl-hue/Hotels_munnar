from django.urls import path
from . import views

urlpatterns = [
    # ── Employee portal ─────────────────────────────
    path('login/',                          views.employee_login,            name='employee_login'),
    path('logout/',                         views.employee_logout,           name='employee_logout'),
    path('dashboard/',                      views.employee_dashboard,        name='employee_dashboard'),
    path('bookings/',                       views.employee_bookings,         name='employee_bookings'),
    path('bookings/<int:pk>/',              views.employee_booking_detail,   name='employee_booking_detail'),
    path('rooms/',                          views.employee_rooms,            name='employee_rooms'),
    path('guests/',                         views.employee_guests,           name='employee_guests'),
    path('reviews/',                        views.employee_reviews,          name='employee_reviews'),
    path('reviews/<int:pk>/delete/',        views.employee_review_delete,    name='employee_review_delete'),
    path('profile/',                        views.employee_profile,          name='employee_profile'),

    # ── Owner: manage employees per hotel ───────────
    path('hotels/<slug:slug>/employees/',           views.manage_employees,  name='manage_employees'),
    path('hotels/<slug:slug>/employees/add/',       views.add_employee,      name='add_employee'),
    path('hotels/<slug:slug>/employees/<int:emp_id>/edit/',   views.edit_employee,   name='edit_employee'),
    path('hotels/<slug:slug>/employees/<int:emp_id>/delete/', views.delete_employee, name='delete_employee'),
    path('hotels/<slug:slug>/employees/<int:emp_id>/toggle/', views.toggle_employee, name='toggle_employee'),
]
