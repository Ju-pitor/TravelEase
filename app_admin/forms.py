from django import forms
from travelers.models import User  # or wherever your User model is
from .models import Destination


class AddAdminForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_app_admin = True
        user.user_type = 'app_admin'
        if commit:
            user.save()
        return user

class DestinationForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = ['name', 'description', 'image', 'location']