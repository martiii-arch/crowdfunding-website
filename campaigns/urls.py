from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views


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

    path('create/',
      views.create_campaign,
        name='create_campaign'),
    path('about/',
      views.about,
        name='about'),

    path('payment-success/', views.payment_success, name='payment_success'),

    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-campaigns/', views.my_campaigns, name='my_campaigns'),
    path('my-donations/', views.my_donations, name='my_donations'),
    path('campaign/<int:campaign_id>/edit/', views.edit_campaign, name='edit_campaign'),
    path('campaign/<int:id>/delete/', views.delete_campaign, name='delete_campaign'),

    path('change-password/', auth_views.PasswordChangeView.as_view(
    template_name='accounts/change_password.html',
    success_url=reverse_lazy('change_password_done')   # 👈 THIS WAS MISSING
    ), name='change_password'),

    path('change-password-done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name='change_password_done'),

]