from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ShopAdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=255)
    address = models.TextField()
    location = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    status = models.BooleanField(default=False)  # False means disabled
    is_active = models.BooleanField(default=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    validity = models.CharField(max_length=20, default='payment pending')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.shop_name

class UploadedImage(models.Model):
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    display_order = models.PositiveIntegerField(default=0)
    shop_admin_profile = models.ForeignKey(ShopAdminProfile, on_delete=models.CASCADE, related_name='uploaded_images')

    def __str__(self):
        return self.image.name

    class Meta:
        ordering = ['display_order', '-uploaded_at']


