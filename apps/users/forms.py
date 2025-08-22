from django import forms
from django.contrib.auth.models import User
from core.models import UserProfile

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "is_active", "is_staff"]

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["avatar", "bio", "phone", "address"]

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "is_active", "is_staff"]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'email': forms.EmailInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'first_name': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'last_name': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["phone", "address"]
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'address': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
        }