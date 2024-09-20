from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ShopAdminLoginForm, ImageUploadForm
from .models import ShopAdminProfile, UploadedImage
from django.contrib.auth import logout
from django.utils import timezone
from threading import Timer
from datetime import timedelta

def index(request):
    if not request.user.is_authenticated:
        return redirect('shop_admin_login')

    shop_admin = request.user.shopadminprofile
    images = UploadedImage.objects.filter(shop_admin_profile=shop_admin)
    return render(request, 'app1/index.html', {'images': images})

@login_required
def shop_admin_dashboard(request):
    shop_admin = get_object_or_404(ShopAdminProfile, user=request.user)
    
    if not shop_admin.status:
        logout(request)
        messages.error(request, 'Your account is currently disabled. Please contact the administrator.')
        return redirect('shop_admin_login')
    
    if shop_admin.validity != 'running':
        messages.warning(request, 'Your payment is pending. Some features may be limited.')
    
    images = UploadedImage.objects.filter(shop_admin_profile=shop_admin)

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_image = form.save(commit=False)
            new_image.shop_admin_profile = shop_admin
            new_image.display_order = UploadedImage.objects.filter(shop_admin_profile=shop_admin).count() + 1
            new_image.save()
            messages.success(request, 'Image uploaded successfully!')
            return redirect('shop_admin_dashboard')
    else:
        form = ImageUploadForm()

    return render(request, 'app1/shop_admin_dashboard.html', {
        'form': form,
        'images': images,
        'shop_admin': shop_admin
    })

def shop_admin_login(request):
    if request.method == 'POST':
        form = ShopAdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                try:
                    shop_admin_profile = ShopAdminProfile.objects.get(user=user)
                    if shop_admin_profile.status:  # Check if the account is enabled
                        login(request, user)
                        return redirect('shop_admin_dashboard')
                    else:
                        messages.error(request, 'Your account is currently disabled. Please contact the administrator.')
                except ShopAdminProfile.DoesNotExist:
                    messages.error(request, 'User does not have a shop admin profile.')
            else:
                messages.error(request, 'Invalid credentials. Please try again.')
    else:
        form = ShopAdminLoginForm()

    return render(request, 'app1/shop_admin_login.html', {'form': form})

@login_required
def delete_image(request, image_id):
    image = get_object_or_404(UploadedImage, id=image_id)
    if request.method == 'POST':
        image.delete()
        messages.success(request, 'Image deleted successfully.')
        return redirect('shop_admin_dashboard')
    return render(request, 'app1/confirm_delete.html', {'image': image})

@login_required
def toggle_featured(request, image_id):
    image = get_object_or_404(UploadedImage, id=image_id)
    image.is_featured = not image.is_featured
    image.save()
    messages.success(request, 'Image featured status updated.')
    return redirect('shop_admin_dashboard')

@login_required
def shop_admin_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('shop_admin_login')

@login_required
def upload_image(request):
    shop_admin_profile = get_object_or_404(ShopAdminProfile, user=request.user)

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_image = form.save(commit=False)
            new_image.shop_admin_profile = shop_admin_profile  # Assign the shop admin profile here
            new_image.save()
            return redirect('shop_admin_dashboard')
    else:
        form = ImageUploadForm()

    return render(request, 'app1/upload_image.html', {'form': form})

def create_shop_admin(request):
    if request.method == 'POST':
        form = ShopAdminLoginForm(request.POST)
        if form.is_valid():
            shop_admin_profile = form.save(commit=False)
            shop_admin_profile.status = False  # Initially disabled
            shop_admin_profile.validity = 'payment pending'
            shop_admin_profile.created_at = timezone.now()
            shop_admin_profile.save()

            # Set a timer to update the status after 1 minute
            Timer(60, enable_status, [shop_admin_profile]).start()

            messages.success(request, 'Shop admin created successfully!')
            return redirect('shop_admin_dashboard')
    else:
        form = ShopAdminLoginForm()

    return render(request, 'app1/create_shop_admin.html', {'form': form})

def enable_status(shop_admin_profile):
    shop_admin_profile.status = True
    shop_admin_profile.validity = 'running'  # Update validity
    shop_admin_profile.save()
