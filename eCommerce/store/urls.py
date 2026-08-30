from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register_buyer/', views.register_buyer, name='register_buyer'),
    path('register_vendor/', views.register_vendor, name='register_vendor'),
    path('register/', views.register, name='register'),
    path('update_user/', views.update_user, name='update_user'),
    path('update_password/', views.update_password, name='update_password'),
    path('update_info', views.update_info, name='update_info'),
    path('product/<int:pk>/', views.product, name='product'),
    path('store/<str:pk>/', views.store, name='store'),
    path('store_summary/', views.store_summary, name='store_summary'),
    path('become_vendor/', views.become_vendor, name='become_vendor'),
    path('become_buyer/', views.become_buyer, name='become_buyer'),
    path('add_store/', views.add_store, name='add_store'),
    path('edit_store/<int:pk>', views.edit_store, name='edit_store'),
    path('delete_store/<int:pk>/', views.delete_store, name='delete_store'),
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/<int:pk>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:pk>/', views.delete_product, name='delete_product'),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='store/password_reset.html'), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='store/password_reset_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='store/password_reset_form.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='store/password_reset_done.html'), name='password_reset_complete'),

    ]