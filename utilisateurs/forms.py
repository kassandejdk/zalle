from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Level


class UserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = [ 
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        ]
        

    
class ProfileForm(forms.ModelForm):
    phone_number = forms.CharField(required=True)
    level = forms.ModelChoiceField(queryset=Level.objects.all(), required=True)
    
    class Meta:
        model = Profile
        fields = [
            
            'phone_number',
            'level',
            'type_profile'
        ]
        widgets = {
            'level': forms.Select(attrs={'class': 'form-control'}),
        }

class LoginForm(forms.Form):
    username = forms.CharField(max_length=254, label='Nom d\'utilisateur, Email ou Numéro de téléphone')
    password = forms.CharField(widget=forms.PasswordInput, label='Mot de passe')
    otp = forms.CharField(max_length=6, required=False, label='Enter OTP')  # Set required to False

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not User.objects.filter(username=username).exists() and not User.objects.filter(email=username).exists() and not User.objects.filter(profile__phone_number=username).exists():
            raise forms.ValidationError("Aucun utilisateur avec ces informations n'a été trouvé.")
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        return password
    

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']