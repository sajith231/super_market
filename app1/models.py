from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import timedelta

    

class ShopAdminProfile(models.Model):
    VALIDITY_CHOICES = [
        ('running', 'Running'),
        ('payment pending', 'Payment Pending'),
        # Add other validity statuses as needed
    ]
    instagram_link = models.URLField(max_length=200, blank=True, null=True)
    facebook_link = models.URLField(max_length=200, blank=True, null=True)
    whatsapp_link = models.URLField(max_length=200, blank=True, null=True)
    google_link = models.URLField(max_length=200, blank=True, null=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=255)
    address = models.TextField()
    location = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    status = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    validity = models.CharField(max_length=20, choices=VALIDITY_CHOICES, default='running')
    created_at = models.DateTimeField(default=timezone.now)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    responsible_person = models.CharField(max_length=255, null=True, blank=True)
    uid = models.CharField(max_length=20, unique=True, blank=True, null=True)
    logo = models.ImageField(upload_to='shop_logos/', blank=True, null=True)
    expiry_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = get_random_string(20)
        if self.validity == 'payment pending':
            self.status = False
        if not self.expiry_date:
            self.expiry_date = timezone.now() + timedelta(days=365)
        super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = get_random_string(20)
        if self.validity == 'payment pending':
            self.status = False
        super().save(*args, **kwargs)

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


