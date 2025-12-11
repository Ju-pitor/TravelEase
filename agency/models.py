from django.db import models
from django.conf import settings
from app_admin.models import Destination
from django.utils import timezone


class AgencyProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    agency_name = models.CharField(max_length=150)
    registration_number = models.CharField(max_length=100)
    agency_address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    contact_email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return self.agency_name

PACKAGE_TYPES = [
    ('single', 'Single'),
    ('couple', 'Couple'),
    ('friends', 'Friends'),
    ('group', 'Group'),
]

class Travelpackage(models.Model):
    agency = models.ForeignKey(AgencyProfile, on_delete=models.CASCADE, related_name='packages')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='packages')
    package_name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50, help_text="e.g. 5 Days / 4 Nights")
    description = models.TextField()
    image = models.ImageField(upload_to='packages/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    people_count=models.PositiveIntegerField(default=1)
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPES, null=True, blank=True)
    climate = models.CharField(max_length=50, blank=True, null=True)  # e.g. 'cold', 'warm', 'tropical'
    activity_type = models.CharField(max_length=50, blank=True, null=True)  # e.g. 'adventure', 'relaxation'



    def __str__(self):
        return f"{self.package_name} - {self.destination.name}"

class Booking(models.Model):
    traveler = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    package = models.ForeignKey(Travelpackage, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    travel_date = models.DateField(default=timezone.now) 
    number_of_people = models.PositiveIntegerField(default=1)
    rejected_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Rejected', 'Rejected'),
        ('Paid', 'Paid'),
        ('Checked-In', 'Checked-In'),
        ('Completed', 'Completed'),
    ], default='Pending')
    
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)  

    def __str__(self):
        return f"{self.traveler.username} - {self.package.package_name} ({self.status})"
    

class ChatMessage(models.Model):
   booking = models.ForeignKey('agency.Booking', on_delete=models.CASCADE, related_name='messages')
   sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
   message = models.TextField()
   timestamp = models.DateTimeField(auto_now_add=True)
   razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)

   
   def __str__(self):
        return f"{self.sender.username}: {self.message[:30]}"