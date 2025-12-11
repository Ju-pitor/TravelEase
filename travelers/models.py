from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from app_admin.models import Destination
from agency.models import Travelpackage

phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('traveler', 'Traveler'),
        ('agency', 'Agency'),
        ('app_admin', 'App Admin'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='traveler')
    is_traveler = models.BooleanField(default=False)
    is_agency = models.BooleanField(default=False)
    is_app_admin = models.BooleanField(default=False) 

    def __str__(self):
        return self.username

class TravelerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

class TravelPlan(models.Model):
    traveler = models.ForeignKey(TravelerProfile, on_delete=models.CASCADE)
    destination = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.destination} ({self.start_date} - {self.end_date})"
    

class Wishlist(models.Model):
    traveler = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    package = models.ForeignKey('agency.Travelpackage', on_delete=models.CASCADE, null=True, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
         if self.package:
            return f"{self.traveler.username} - {self.package.package_name}"
         elif self.destination:
            return f"{self.traveler.username} - {self.destination.name}"
         return self.traveler.username
    

class DestinationRating(models.Model):
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='ratings')
    traveler = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=0)
    review = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('destination', 'traveler')

    def __str__(self):
        return f"{self.destination.name} - {self.rating}/5 by {self.traveler.username}"


class PackageRating(models.Model):
    package = models.ForeignKey('agency.Travelpackage', on_delete=models.CASCADE, related_name='ratings')
    traveler = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=0)
    review = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('package', 'traveler')

    def __str__(self):
        return f"{self.package.package_name} - {self.rating}/5 by {self.traveler.username}"
