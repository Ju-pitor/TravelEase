from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_agency, name='register_agency'),
    path('dashboard/', views.agency_dashboard, name='agency_dashboard'),
    path('add-package/', views.add_package, name='add_package'),
    path('edit-package/<int:package_id>/', views.edit_package, name='edit_package'),
    path('delete-package/<int:package_id>/', views.delete_package, name='delete_package'),
    path('packages/<int:destination_id>/', views.destination_packages, name='destination_packages'),

    path('package/<int:package_id>/', views.package_detail, name='package_detail'),
    path('agency/<int:agency_id>/', views.agency_detail, name='agency_detail'),

    path('bookings/', views.manage_bookings, name='manage_bookings'),
    path('update_bookings/<int:booking_id>/<str:action>/', views.update_booking_status, name='update_booking_status'),
    path('chat/<int:booking_id>/', views.chat_view, name='chat'),
    path('mark_complete/<int:booking_id>/',views.agency_mark_completed,name='mark_completed'),
    path('view_reciept/<int:id>/',views.agency_view_receipt,name="view_reciept"),
    path('viewhistory/',views.agency_booking_history,name='agency_history')
]
