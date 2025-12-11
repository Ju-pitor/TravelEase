from django import forms
from django.contrib.auth.forms import UserCreationForm
from travelers.models import User  # use the same User model
from .models import AgencyProfile,Travelpackage,Booking

class AgencyRegisterForm(UserCreationForm):
    agency_name = forms.CharField(max_length=150, help_text="This will be your username for login")
    registration_number = forms.CharField(max_length=100)
    email = forms.EmailField(required=True)
    address = forms.CharField(max_length=255, required=False)
    phone_number = forms.CharField(max_length=20, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ['agency_name', 'email', 'password1', 'password2',
        'registration_number', 'address', 'phone_number', 'description']

    def clean(self):
        cleaned_data = super().clean()
        agency_name = cleaned_data.get('agency_name')
        
        if agency_name and User.objects.filter(username=agency_name).exists():
            self.add_error('agency_name', 'An agency with this name already exists.')
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['agency_name']
        user.email = self.cleaned_data['email']
        user.is_agency = True

        if commit:
            user.save()
            AgencyProfile.objects.create(
                user=user,
                agency_name=self.cleaned_data['agency_name'],
                registration_number=self.cleaned_data['registration_number'],
                agency_address=self.cleaned_data.get('address')or'',
                phone_number=self.cleaned_data.get('phone_number')or'',
                description=self.cleaned_data.get('description')or'',
                contact_email =self.cleaned_data.get('email')or'',
            )
        return user

class TravelpackageForm(forms.ModelForm):
    class Meta:
        model = Travelpackage
        fields = ['destination','package_name','price','duration','description','image','people_count','package_type','climate','activity_type']
        widgets = {
            'package_type': forms.Select(attrs={'class': 'form-input'}),
        }


