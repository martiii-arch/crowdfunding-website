from django.urls import path
from . import views

urlpatterns = [

    # Home
    path('', views.home, name='home'),

    # Explore campaigns
    path('explore/', views.explore, name='explore'),

    # Campaign detail
    path('campaign/<int:campaign_id>/',
    views.campaign_detail,
    name='campaign_detail'),

    # Donation page (GET + POST handled here)
    path('campaign/<int:campaign_id>/donate/',
    views.donate,
    name='donate'),

    # Authentication
    path('login/',
    views.login_view,
    name='login'),

    path('register/',
    views.register,
    name='register'),

    path('logout/',
views.logout_view,
name='logout'),


]