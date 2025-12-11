"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_traveler, name='register_traveler'),
    path('dashboard/', views.traveler_dashboard, name='traveler_dashboard'),
    path('login/', views.common_login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('submit-grievance/', views.submit_grievance, name='submit_grievance'),
    path('plan/edit/<int:id>/', views.edit_plan, name='edit_plan'),
    path('plan/delete/<int:id>/', views.delete_plan, name='delete_plan'),
    path("add_plan/",views.add_plan,name='add_plan'),
    path('destination/<int:pk>/', views.destination_detail, name='destination_detail'),
    path('wishlist/add/<str:item_type>/<int:item_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('quiz/', views.travel_quiz, name='travel_quiz'),
    path('rate_package/<int:id>',views.rate_package,name='rate_package'),
    path('rate_destination/<int:id>',views.rate_destination,name='rate_destination'),
    path('book/<int:package_id>', views.book_package, name='book_package'),
    path('my-bookings/', views.traveler_bookings, name='traveler_bookings'),
    path('view_package/',views.view_packages,name="view_packages"),
    path('api/bookings/status/', views.get_latest_booking_status, name='get_latest_booking_status'),
    path('payment/<int:booking_id>/', views.payment_page, name='payment_page'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('receipt/<int:id>/', views.view_receipt, name='view_receipt'),
    path('check_in/<int:booking_id>/',views.check_in,name="check_in"),
    path('history',views.booking_history,name="booking_history"),
    path("receipt/download/<int:id>/", views.download_receipt, name="download_receipt"),
    path("cancel-booking/<int:id>/",views.cancel_booking,name="cancel_booking"),



]