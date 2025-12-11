from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.app_admin_dashboard, name='app_admin_dashboard'),
    path('addadmin/', views.add_app_admin, name='add_app_admin'),
    path('add_agency/',views.add_agency,name='add_agency'),
    path('add_traveler/',views.add_traveler,name='add_traveler'),
    path('add-destination/', views.add_destination, name='add_destination'),

    path('manage-destinations/', views.manage_destinations, name='manage_destinations'),
    path('edit-destination/<int:pk>/', views.edit_destination, name='edit_destination'),
    path('delete-destination/<int:pk>/', views.delete_destination, name='delete_destination'),
    path('grievance/resolve/<int:grievance_id>/', views.resolve_grievance, name='resolve_grievance'),


]

