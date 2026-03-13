from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('approval-pending/', views.approval_pending_view, name='approval_pending'),
    # Admin approval views
    path('admin/owner-approvals/', views.owner_approval_list, name='owner_approval_list'),
    path('admin/owner-approvals/<int:profile_id>/approve/', views.approve_owner, name='approve_owner'),
    path('admin/owner-approvals/<int:profile_id>/reject/', views.reject_owner, name='reject_owner'),
]
