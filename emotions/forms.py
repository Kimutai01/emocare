from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Profile

class UpdateUserForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['email']

class UpdateProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['name','avatar','email']

