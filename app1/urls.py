
from django.urls import path
from app1 import views  # Import the views from your app
from .views import shop_admin_logout




urlpatterns = [
    path('', views.index, name='index'),  # Home page
    path('shopadminlogin/', views.shop_admin_login, name='shop_admin_login'),  # Shop admin login
    path('shop_admin/logout/', shop_admin_logout, name='shop_admin_logout'),
    path('upload/', views.UploadedImage),  # Corrected reference to upload_image
    path('delete/<int:image_id>/', views.delete_image, name='delete_image'),  # Corrected reference to delete_image
    path('toggle-featured/<int:image_id>/', views.toggle_featured, name='toggle_featured'),
    path('delete-image/<int:image_id>/', views.delete_image, name='delete_image'),
    path('shop-admin-dashboard/', views.shop_admin_dashboard, name='shop_admin_dashboard'),


    path('', views.index, name='index'),  # Home page
    path('shopadminlogin/', views.shop_admin_login, name='shop_admin_login'),  # Shop admin login
    path('shop-admin-dashboard/', views.shop_admin_dashboard, name='shop_admin_dashboard'),
    path('delete/<int:image_id>/', views.delete_image, name='delete_image'),
    path('toggle-featured/<int:image_id>/', views.toggle_featured, name='toggle_featured'),
]
