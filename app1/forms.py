from django import forms
from django.contrib.auth import authenticate
from .models import UploadedImage,ShopAdminProfile
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password 

class ShopAdminLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Enter your username',
            'autocomplete': 'username',
        }),
        label="Username"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
        }),
        label="Password"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""  # Removes : from the end of labels

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError('Invalid credentials', code='invalid_login')

        return cleaned_data

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        labels = {
            'image': 'Upload Image',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""  # Removes : from the end of labels



class ShopAdminProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=False)  # Optional field

    class Meta:
        model = ShopAdminProfile
        fields = ['shop_name', 'address', 'location', 'phone_number', 'amount', 'responsible_person', 'username', 'password']
        widgets = {
            'shop_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'responsible_person': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            return make_password(password)  # Hash the password if provided
        return None  # Return None to not change the password
    



class ShopAdminCreationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    shop_name = forms.CharField(max_length=100, required=True)
    address = forms.CharField(max_length=255, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    location = forms.CharField(max_length=100, required=True)  # New Location field
    amount = forms.DecimalField(max_digits=10, decimal_places=2, required=True)  # New Amount field

    class Meta:
        model = ShopAdminProfile
        fields = ['shop_name', 'address', 'location', 'phone_number', 'amount']  # Updated fields list

    def save(self, commit=True):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = User.objects.create_user(username=username, password=password)

        # Create the shop admin profile
        shop_admin_profile = super(ShopAdminCreationForm, self).save(commit=False)
        shop_admin_profile.user = user  # Link the new user to the shop admin profile
        shop_admin_profile.validity = 'running'  # Set validity to Running

        if commit:
            shop_admin_profile.save()

        return shop_admin_profile