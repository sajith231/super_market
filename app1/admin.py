from django.contrib import admin
from .models import ShopAdminProfile, UploadedImage
from django.urls import path
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.contrib import messages
from django.middleware.csrf import get_token
from django.utils import timezone

class UploadedImageInline(admin.TabularInline):
    model = UploadedImage
    extra = 1

class ShopAdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'shop_name', 'address', 'location', 'phone_number', 'amount', 'validity', 'status_button')
    search_fields = ('user__username', 'shop_name')
    list_filter = ('shop_name', 'status', 'validity')
    ordering = ('shop_name',)
    inlines = [UploadedImageInline]

    def get_queryset(self, request):
        self.request = request
        return super().get_queryset(request)

    def status_button(self, obj):
        status_text = "Enabled" if obj.status else "Disabled"
        button_color = "green" if obj.status else "red"
        new_status = 0 if obj.status else 1
        
        return format_html(
            '<form action="{}" method="post" style="display:inline;">'
            '<input type="hidden" name="csrfmiddlewaretoken" value="{}">'
            '<input type="hidden" name="status" value="{}">'
            '<button type="submit" style="color: {}; font-weight: bold;">{}</button>'
            '</form>',
            self.get_action_url(obj), get_token(self.request), new_status, button_color, status_text
        )
    status_button.short_description = 'Status'

    def get_action_url(self, obj):
        return f'/admin/app1/shopadminprofile/{obj.id}/toggle_status/'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:profile_id>/toggle_status/', self.admin_site.admin_view(self.toggle_status), name='toggle_status'),
        ]
        return custom_urls + urls

    def toggle_status(self, request, profile_id):
        profile = self.get_object(request, profile_id)
        if request.method == 'POST':
            new_status = request.POST.get('status') == '1'
            profile.status = new_status
            profile.save()
            messages.success(request, f'Status updated to {"Enabled" if profile.status else "Disabled"}')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/'))

    def save_model(self, request, obj, form, change):
        if not change:  # This is a new object
            obj.status = False  # Set initial status to disabled
        super().save_model(request, obj, form, change)

admin.site.register(ShopAdminProfile, ShopAdminProfileAdmin)
admin.site.register(UploadedImage)
