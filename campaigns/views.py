from django.shortcuts import render, get_object_or_404, redirect
from .models import Campaign, Donation
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from decimal import Decimal



def home(request):

    campaigns = Campaign.objects.all()[:3]

    for c in campaigns:

        if c.goal_amount > 0:

            c.progress = (c.amount_raised / c.goal_amount) * 100

        else:

            c.progress = 0

    return render(request,'campaigns/home.html',{
        'campaigns':campaigns
    })


def campaign_detail(request, campaign_id):

    campaign = get_object_or_404(Campaign,id=campaign_id)

    if campaign.goal_amount > 0:

        campaign.progress = (campaign.amount_raised / campaign.goal_amount) * 100

    else:

        campaign.progress = 0

    donations = Donation.objects.filter(
        campaign=campaign
    ).order_by('-donated_at')[:5]

    return render(request,
    'campaigns/campaign_detail.html',{

        'campaign':campaign,
        'donations':donations

    })


def explore(request):

    campaigns = Campaign.objects.all()

    for c in campaigns:

        if c.goal_amount > 0:

            c.progress = (c.amount_raised / c.goal_amount) * 100

        else:

            c.progress = 0

    return render(request,
    'campaigns/explore.html',{

        'campaigns':campaigns

    })


# LOGIN VIEW (FIXED)

def login_view(request):

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request,user)

            messages.success(
                request,
                "Login successful"
            )

            return redirect('home')

        else:

            messages.error(
                request,
                "Invalid username or password"
            )

    return render(request,
    'campaigns/login.html')


# REGISTER VIEW (FIXED)

def register(request):

    if request.method == "POST":

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')

        if password != confirm:

            messages.error(
                request,
                "Passwords do not match"
            )

            return redirect('register')

        if User.objects.filter(username=username).exists():

            messages.error(
                request,
                "Username already exists"
            )

            return redirect('register')

        if User.objects.filter(email=email).exists():

            messages.error(
                request,
                "Email already registered"
            )

            return redirect('register')

        user = User.objects.create_user(

            username=username,
            email=email,
            password=password

        )

        # AUTO LOGIN AFTER REGISTER (professional feature)

        login(request,user)

        messages.success(
            request,
            "Account created successfully"
        )

        return redirect('home')

    return render(request,
    'campaigns/register.html')


# DONATION VIEW

@login_required
def donate(request, campaign_id):

    campaign = get_object_or_404(Campaign,id=campaign_id)

    if request.method == "POST":

        amount = request.POST.get('amount')

        if amount and float(amount) > 0:

            Donation.objects.create(

    campaign=campaign,
    donor=request.user,
    amount=amount

            )

            campaign.amount_raised += Decimal(amount)

            campaign.save()

            messages.success(

                request,
                "Thank you for your donation!"

            )

            return redirect(
                'campaign_detail',
                campaign_id=campaign.id
            )

        else:

            messages.error(
                request,
                "Enter valid amount"
            )

    return render(request,
    'campaigns/donation_page.html',{

        'campaign':campaign

    })

from django.contrib.auth import logout

def logout_view(request):

    logout(request)

    messages.success(
        request,
        "Logged out successfully"
    )

    return redirect('home')