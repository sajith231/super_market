from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required         
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone
from .forms import ShopAdminLoginForm, ImageUploadForm, ShopAdminProfileForm,ShopAdminCreationForm
from .models import ShopAdminProfile, UploadedImage,UploadedImage
from threading import Timer
from .models import UploadedImage, ShopAdminProfile
import threading
import qrcode
from django.utils.crypto import get_random_string
import os
from django.conf import settings
from django.urls import reverse
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ShopAdminProfile
import os
from django.db import IntegrityError
from django.contrib.auth.models import User
import time
from urllib.parse import urljoin
from datetime import timedelta

def login_view(request):
    if request.method == 'POST':
        form = ShopAdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_superuser:
                    login(request, user)
                    return redirect('superuser_dashboard')
                else:
                    try:
                        shop_admin_profile = ShopAdminProfile.objects.get(user=user)
                        if shop_admin_profile.status:
                            login(request, user)
                            return redirect('shop_admin_dashboard')
                        else:
                            messages.error(request, 'Your account is currently disabled. Please contact the administrator.')
                    except ShopAdminProfile.DoesNotExist:
                        messages.error(request, 'User does not have a shop admin profile.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = ShopAdminLoginForm()

    return render(request, 'shop_admin_login.html', {'form': form})


@login_required
def shop_admin_dashboard(request):
    shop_admin = get_object_or_404(ShopAdminProfile, user=request.user)
    
    if request.method == 'POST':
        if 'upload_logo' in request.POST:
            if request.FILES.get('shop_logo'):
                shop_admin.logo = request.FILES['shop_logo']
                shop_admin.save()
        elif 'upload_image' in request.POST:
            form = ImageUploadForm(request.POST, request.FILES)
            if form.is_valid():
                new_image = form.save(commit=False)
                new_image.shop_admin_profile = shop_admin
                new_image.display_order = UploadedImage.objects.filter(shop_admin_profile=shop_admin).count() + 1
                new_image.save()
            else:
                messages.error(request, 'Error uploading image. Please check the file format and try again.')
                print("Form errors:", form.errors)  # debugging print for errors
        elif 'generate_qr' in request.POST:
            return generate_qr_code(request)
    
    # Generate the production URL for display
    protocol = 'https://' if settings.PRODUCTION_SERVER.get('USE_HTTPS') else 'http://'
    server_ip = settings.PRODUCTION_SERVER.get('IP')
    server_port = settings.PRODUCTION_SERVER.get('PORT')
    base_url = f"{protocol}{server_ip}:{server_port}"
    index_path = reverse('index_with_uid', kwargs={'uid': shop_admin.uid})
    production_url = urljoin(base_url, index_path)
    
    context = {
        'form': ImageUploadForm(),
        'images': shop_admin.uploaded_images.all(),
        'shop_admin': shop_admin,
        'qr_code_url': production_url,
        'can_edit': shop_admin.validity != 'payment pending',
    }
    
    return render(request, 'shop_admin_dashboard.html', context)



def generate_qr_code_async(request, shop_admin_id):
    from django.urls import reverse
    from django.utils.crypto import get_random_string
    import qrcode
    import os
    from django.conf import settings

    shop_admin = ShopAdminProfile.objects.get(id=shop_admin_id)     #34567876545678765678765678765
    
    if not shop_admin.uid:
        shop_admin.uid = get_random_string(length=20)
        shop_admin.save()
    
    index_url = request.build_absolute_uri(reverse('index_with_uid', kwargs={'uid': shop_admin.uid}))
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(index_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    qr_code_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
    os.makedirs(qr_code_dir, exist_ok=True)
    file_name = f'qr_code_{shop_admin.uid}.png'
    file_path = os.path.join(qr_code_dir, file_name)
    img.save(file_path)
    
    shop_admin.qr_code = os.path.join('qr_codes', file_name)
    shop_admin.save()
    

@login_required
def superuser_dashboard(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You don't have permission to access this page.")

    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    shop_admin_profiles = ShopAdminProfile.objects.all()

    if search_query:
        shop_admin_profiles = shop_admin_profiles.filter(shop_name__icontains=search_query)

    if status_filter:
        if status_filter == 'enabled':
            shop_admin_profiles = shop_admin_profiles.filter(status=True)
        elif status_filter == 'disabled':
            shop_admin_profiles = shop_admin_profiles.filter(status=False)

    for profile in shop_admin_profiles:
        if profile.expiry_date:
            profile.days_until_expiry = (profile.expiry_date - timezone.now()).days

    return render(request, 'superuser_dashboard.html', {
        'shop_admin_profiles': shop_admin_profiles,
        'search_query': search_query,
        'status_filter': status_filter
    })




def change_validity_after_365_days(profile_id):
    
    time.sleep(365 * 24 * 60 * 60)  
    try:
        profile = ShopAdminProfile.objects.get(id=profile_id)
        profile.validity = 'payment pending'
        profile.save()  # This will trigger the save method in the model, which sets status to False
    except ShopAdminProfile.DoesNotExist:
        pass

@login_required
def create_shop_admin(request): 
    if not request.user.is_superuser:
        return HttpResponseForbidden("You don't have permission to access this page.")

    if request.method == 'POST':
        form = ShopAdminCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            if User.objects.filter(username=username).exists():
                messages.error(request, f"Username '{username}' already exists. Please choose a different username.")
                return render(request, 'create_shop_admin.html', {'form': form})

            try:
                shop_admin_profile = form.save(commit=False)
                shop_admin_profile.status = True
                shop_admin_profile.validity = 'running'  # Set validity to running
                shop_admin_profile.save()

                # Start a thread to change the validity status after 365 days
                threading.Thread(target=change_validity_after_365_days, args=(shop_admin_profile.id,)).start()

                messages.success(request, 'New Shop Admin created successfully!')
                return redirect('superuser_dashboard')
            except Exception as e:
                messages.error(request, f'An error occurred while creating the shop admin: {str(e)}')
    else:
        form = ShopAdminCreationForm()

    return render(request, 'create_shop_admin.html', {'form': form})



@login_required
def edit_shop_admin(request, profile_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You don't have permission to access this page.")

    # Get the shop admin profile or return 404
    profile = get_object_or_404(ShopAdminProfile, id=profile_id)
    
    if request.method == 'POST':
        form = ShopAdminProfileForm(request.POST, instance=profile)
        if form.is_valid():
            try:
                # Get or create associated user
                if hasattr(profile, 'user') and profile.user:
                    user = profile.user
                else:
                    # Create new user if none exists
                    username = form.cleaned_data['username']
                    if User.objects.filter(username=username).exists():
                        messages.error(request, f"Username '{username}' already exists. Please choose a different username.")
                        return render(request, 'edit_shop_admin.html', {'form': form, 'profile': profile})
                    
                    user = User.objects.create_user(
                        username=username,
                        password=form.cleaned_data.get('password', get_random_string(12))
                    )
                    profile.user = user
                
                # Update user details
                user.username = form.cleaned_data['username']
                if form.cleaned_data.get('password'):
                    user.set_password(form.cleaned_data['password'])
                user.save()
                
                # Save profile
                profile_instance = form.save(commit=False)
                profile_instance.user = user
                profile_instance.save()
                
                messages.success(request, 'Shop admin profile updated successfully!')
                return redirect('superuser_dashboard')
                
            except Exception as e:
                messages.error(request, f'An error occurred while updating the profile: {str(e)}')
                return render(request, 'edit_shop_admin.html', {'form': form, 'profile': profile})
    else:
        # Initialize form with existing data
        initial_data = {
            'username': profile.user.username if hasattr(profile, 'user') and profile.user else '',
            'shop_name': profile.shop_name,
            'location': profile.location,
            'address': profile.address,
            'phone_number': profile.phone_number,
            'amount': profile.amount,
            'responsible_person': profile.responsible_person,
        }
        form = ShopAdminProfileForm(initial=initial_data)

    return render(request, 'edit_shop_admin.html', {
        'form': form, 
        'profile': profile,
        'has_user': hasattr(profile, 'user') and profile.user is not None
    })


@login_required
def toggle_status(request, profile_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    profile = get_object_or_404(ShopAdminProfile, id=profile_id)
    profile.status = not profile.status
    
    if profile.status:  # If the profile is being enabled
        profile.validity = 'running'
        profile.expiry_date = timezone.now() + timedelta(days=365)  # Set expiry to one year from now
        # Start a thread to change the validity status after one year
        threading.Thread(target=change_validity_after_365_days, args=(profile.id,)).start()
    else:
        profile.expiry_date = None  # Clear the expiry date when disabling
    
    profile.save()
    status_text = "enabled" if profile.status else "disabled"
    messages.success(request, f'Shop admin account has been {status_text}.')
    return redirect('superuser_dashboard')
    

@login_required
def delete_image(request, image_id):
    image = get_object_or_404(UploadedImage, id=image_id)
    if request.method == 'POST':
        image.delete()
        return redirect('shop_admin_dashboard')
    return render(request, 'confirm_delete.html', {'image': image})



@login_required
def toggle_status(request, profile_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    profile = get_object_or_404(ShopAdminProfile, id=profile_id)
    profile.status = not profile.status
    
    if profile.status:  # If the profile is being enabled
        profile.validity = 'running'
        if not profile.expiry_date:  # Only set expiry_date if it's not already set
            profile.expiry_date = timezone.now() + timedelta(days=365)
        # Start a thread to change the validity status after one year
        threading.Thread(target=change_validity_after_365_days, args=(profile.id,)).start()
    
    profile.save()
    status_text = "enabled" if profile.status else "disabled"
    messages.success(request, f'Shop admin account has been {status_text}.')
    return redirect('superuser_dashboard')


def shop_admin_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('shop_admin_login')


def superuser_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('shop_admin_login')


@login_required
def upload_image_view(request):  # Changed the name from `UploadedImage` to `upload_image_view`
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_image = form.save(commit=False)
            shop_admin_profile = ShopAdminProfile.objects.get(user=request.user)
            new_image.shop_admin_profile = shop_admin_profile
            new_image.display_order = UploadedImage.objects.filter(shop_admin_profile=shop_admin_profile).count() + 1
            new_image.save()
            messages.success(request, 'Image uploaded successfully!')
            return redirect('shop_admin_dashboard')
    else:
        form = ImageUploadForm()
    
    return render(request, 'upload_image.html', {'form': form})


@login_required
def index(request):
    try:
        # Get the logged-in user's shop admin profile
        shop_admin_profile = ShopAdminProfile.objects.get(user=request.user)

        # Retrieve only the images uploaded by this shop admin
        images = UploadedImage.objects.filter(shop_admin_profile=shop_admin_profile)

        return render(request, 'index.html', {'images': images, 'shop_admin': shop_admin_profile})
    
    except ShopAdminProfile.DoesNotExist:
        # If the user doesn't have a shop admin profile, redirect them or show an error
        return redirect('shop_admin_login')
    

@login_required
def delete_shop_admin(request, profile_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    try:
        profile = ShopAdminProfile.objects.get(id=profile_id)
        
        if request.method == 'POST':
            user = profile.user
            profile.delete()
            user.delete()  # Delete the associated User object
            messages.success(request, 'Shop admin deleted successfully!')
            return redirect('superuser_dashboard')
        else:
            return render(request, 'confirm_delete_shop_admin.html', {'profile': profile})
    
    except ShopAdminProfile.DoesNotExist:
        messages.error(request, f'Shop admin with ID {profile_id} does not exist.')
        return redirect('superuser_dashboard')



@login_required
def generate_qr_code(request):
    shop_admin = get_object_or_404(ShopAdminProfile, user=request.user)
    
    # Generate or get the UID
    if not shop_admin.uid:
        shop_admin.uid = get_random_string(length=20)
        shop_admin.save()
    
    # Construct the production URL
    protocol = 'https://' if settings.PRODUCTION_SERVER.get('USE_HTTPS') else 'http://'
    server_ip = settings.PRODUCTION_SERVER.get('IP')
    server_port = settings.PRODUCTION_SERVER.get('PORT')
    
    # Build the complete URL with the production server IP
    base_url = f"{protocol}{server_ip}:{server_port}"
    index_path = reverse('index_with_uid', kwargs={'uid': shop_admin.uid})
    production_url = urljoin(base_url, index_path)
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(production_url)
    qr.make(fit=True)
    
    # Create the QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save the QR code image
    qr_code_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
    os.makedirs(qr_code_dir, exist_ok=True)
    file_name = f'qr_code_{shop_admin.uid}.png'
    file_path = os.path.join(qr_code_dir, file_name)
    img.save(file_path)
    
    # Update shop admin profile with QR code path
    shop_admin.qr_code = os.path.join('qr_codes', file_name)
    shop_admin.save()
    
    messages.success(request, f'QR Code generated successfully! URL: {production_url}')
    return redirect('shop_admin_dashboard')


def index_with_uid(request, uid):
    shop_admin = get_object_or_404(ShopAdminProfile, uid=uid)
    images = shop_admin.uploaded_images.all()
    context = {
        'images': images,
        'shop_admin': shop_admin,
        'footer_details': {
            'shop_name': shop_admin.shop_name,
            'address': shop_admin.address,
            'phone_number': shop_admin.phone_number,
            'location': shop_admin.location,
        }
    }
    return render(request, 'index.html', context)



@login_required
def download_qr_code(request):
    shop_admin = get_object_or_404(ShopAdminProfile, user=request.user)
    
    if shop_admin.qr_code:
        file_path = shop_admin.qr_code.path
        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'))
            response['Content-Disposition'] = f'attachment; filename="qr_code_{shop_admin.uid}.png"'
            return response
    
    # If QR code doesn't exist or file is not found, redirect to generate QR code
    return redirect('generate_qr_code')



@login_required
def home(request):
    shop_admin = get_object_or_404(ShopAdminProfile, user=request.user)
    profile_updated = False  # Initialize a flag

    if request.method == 'POST':
        form = ShopAdminProfileForm(request.POST, request.FILES, instance=shop_admin)
        if form.is_valid():
            # Handle username change
            new_username = form.cleaned_data.get('username')
            if new_username and new_username != shop_admin.user.username:
                if User.objects.filter(username=new_username).exclude(id=request.user.id).exists():
                    messages.error(request, 'Username already exists!')
                    return render(request, 'home.html', {'form': form, 'shop_admin': shop_admin})
                shop_admin.user.username = new_username
                shop_admin.user.save()

            # Handle password change
            new_password = form.cleaned_data.get('password')
            if new_password:
                shop_admin.user.set_password(new_password)
                shop_admin.user.save()
                messages.success(request, 'Password updated successfully. Please login again.')
                logout(request)
                return redirect('shop_admin_login')

            # Save other profile changes
            shop_admin = form.save(commit=False)

            # Handle logo upload
            if 'logo' in request.FILES:
                shop_admin.logo = request.FILES['logo']
            
            shop_admin.save()
            messages.success(request, 'Profile updated successfully!')
            profile_updated = True  # Set the flag to True
            return redirect('home')
    else:
        form = ShopAdminProfileForm(instance=shop_admin, initial={
            'username': shop_admin.user.username,
            'instagram_link': shop_admin.instagram_link,
            'facebook_link': shop_admin.facebook_link,
            'whatsapp_link': shop_admin.whatsapp_link,
            'google_link': shop_admin.google_link
           
        })

    context = {
        'form': form,
        'shop_admin': shop_admin,
        'profile_updated': profile_updated,  # Pass the flag to the template
    }
    return render(request, 'home.html', context)



from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def get_expiry_date(profile):
    if profile.expiry_date:
        return profile.expiry_date
    elif profile.created_at:
        return profile.created_at + timedelta(days=365)
    else:
        return timezone.now() + timedelta(days=365)
























































