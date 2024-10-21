from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import UploadedImage, ShopAdminProfile

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
        self.label_suffix = ""

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
        self.label_suffix = ""

class ShopAdminCreationForm(forms.ModelForm):
    shop_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control mb-3', 'rows': 3})
    )
    location = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'})
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'})
    )
    amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control mb-3'})
    )
    responsible_person = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'})
    )

    # Moving username, password, and confirm_password to the end
    username = forms.CharField(
        max_length=150, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control mb-3'}), 
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control mb-3'}),
        required=True,
        label="Confirm Password"
    )

    class Meta:
        model = ShopAdminProfile
        fields = [
            'shop_name', 'address', 'location', 'phone_number', 
            'responsible_person', 'amount', 
            'username', 'password', 'confirm_password'
        ]
        widgets = {
            'shop_name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'address': forms.Textarea(attrs={'class': 'form-control mb-3', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control mb-3'}),
            'responsible_person': forms.TextInput(attrs={'class': 'form-control mb-3'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        username = cleaned_data.get('username')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")

        return cleaned_data

    def save(self, commit=True):                                     
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password']
        )

        shop_admin_profile = super().save(commit=False)
        shop_admin_profile.user = user
        shop_admin_profile.validity = 'running'
        shop_admin_profile.status = True

        if commit:
            shop_admin_profile.save()

        return shop_admin_profile

class ShopAdminProfileForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control mb-3'})
    )
    password = forms.CharField(
        required=False, widget=forms.PasswordInput(attrs={'class': 'form-control mb-3'})
    )
    confirm_password = forms.CharField(
        required=False, widget=forms.PasswordInput(attrs={'class': 'form-control mb-3'})
    )
    instagram_link = forms.URLField(
        required=False, widget=forms.URLInput(attrs={'class': 'form-control mb-3'})
    )
    facebook_link = forms.URLField(
        required=False, widget=forms.URLInput(attrs={'class': 'form-control mb-3'})
    )
    whatsapp_link = forms.URLField(
        required=False, widget=forms.URLInput(attrs={'class': 'form-control mb-3'})
    )
    google_link = forms.URLField(
        required=False, widget=forms.URLInput(attrs={'class': 'form-control mb-3'})
    )

    class Meta:
        model = ShopAdminProfile
        fields = [
            'username', 'shop_name', 'address', 'location', 'phone_number', 'logo',
            'instagram_link', 'facebook_link', 'whatsapp_link', 'google_link'
        ]
        widgets = {
            'shop_name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'address': forms.Textarea(attrs={'class': 'form-control mb-3', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control mb-3'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

class ProfileSettingsForm(forms.ModelForm):
    current_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control mb-3'}),
        help_text='Enter current password to confirm changes'
    )
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control mb-3'}),
        help_text='Leave empty to keep current password'
    )
    confirm_new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control mb-3'})
    )

    class Meta:
        model = ShopAdminProfile
        fields = ['shop_name', 'location', 'address', 'phone_number']
        widgets = {
            'shop_name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'location': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'address': forms.Textarea(attrs={'class': 'form-control mb-3', 'rows': 3}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control mb-3'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get('current_password')
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        if new_password:
            if not current_password:
                raise forms.ValidationError("Please enter your current password to change password")
            if not confirm_new_password:
                raise forms.ValidationError("Please confirm your new password")
            if new_password != confirm_new_password:
                raise forms.ValidationError("New passwords do not match")
            
            if self.instance and self.instance.user:
                if not self.instance.user.check_password(current_password):
                    raise forms.ValidationError("Current password is incorrect")

        return cleaned_data