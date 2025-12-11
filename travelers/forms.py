from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, TravelerProfile,TravelPlan
from agency.models import Booking

class TravelerRegisterForm(UserCreationForm):
    phone_number = forms.CharField(max_length=20)
    country = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2',
                  'phone_number','country']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_traveler = True
        if commit:
            user.save()
            TravelerProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                country=self.cleaned_data['country']
            )
        return user


class TravelPlanForm(forms.ModelForm):
    class Meta:
        model = TravelPlan
        fields = ['destination', 'start_date', 'end_date', 'notes']


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['number_of_people', 'travel_date']
        widgets = {
            'travel_date': forms.DateInput(attrs={'type': 'date'}),
            'number_of_people': forms.NumberInput(attrs={'id': 'numPeople'}),
            
        }
    