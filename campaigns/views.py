from django.shortcuts import render, get_object_or_404, redirect
from .models import Campaign, Donation
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from .forms import CampaignForm, DonationForm
import razorpay




# ---------------- HOME ----------------
def home(request):
    campaigns = Campaign.objects.all()[:6]
    return render(request, 'campaigns/home.html', {
        'campaigns': campaigns
    })


# ---------------- EXPLORE ----------------
def explore(request):
    campaigns = Campaign.objects.all()
    return render(request, 'campaigns/explore.html', {
        'campaigns': campaigns
    })


# ---------------- CAMPAIGN DETAIL ----------------
def campaign_detail(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    donations = Donation.objects.filter(
        campaign=campaign
    ).order_by('-donated_at')[:5]

    return render(request, 'campaigns/campaign_detail.html', {
        'campaign': campaign,
        'donations': donations
    })


# ---------------- LOGIN ----------------
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            if not request.POST.get('remember_me'):
                request.session.set_expiry(0)

            messages.success(request, "Login successful")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'campaigns/login.html')


# ---------------- REGISTER ----------------
def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('register')

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters")
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        login(request, user)
        messages.success(request, "Account created successfully")
        return redirect('home')

    return render(request, 'campaigns/register.html')


# ---------------- DONATE ----------------
@login_required
def donate(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    if request.method == "POST":
        form = DonationForm(request.POST)

        if form.is_valid():
            amount_rupees = int(form.cleaned_data['amount'])
            amount_paise = amount_rupees * 100

            # store in session
            request.session['campaign_id'] = campaign.id
            request.session['amount'] = amount_rupees

            client = razorpay.Client(auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            ))

            order = client.order.create({
                "amount": amount_paise,
                "currency": "INR",
                "payment_capture": 1
            })

            
            callback_url = request.build_absolute_uri('/payment-success/')

            return render(request, "campaigns/payment.html", {
                "campaign": campaign,
                "order_id": order["id"],
                "amount": amount_paise,
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "callback_url": callback_url,
            })
        else:
            messages.error(request, "Please enter a valid donation amount")

    return render(request, 'campaigns/donation_page.html', {
        'campaign': campaign
    })


# ---------------- PAYMENT SUCCESS ----------------
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  
@login_required
def payment_success(request):
    if request.method != "POST":
        return redirect('home')

    payment_id = request.POST.get("razorpay_payment_id", "")
    order_id = request.POST.get("razorpay_order_id", "")
    signature = request.POST.get("razorpay_signature", "")

    client = razorpay.Client(auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    ))

    
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature,
        })
    except razorpay.errors.SignatureVerificationError:
        messages.error(request, "Payment verification failed. Please contact support.")
        return redirect('home')

    # Get amount and campaign from session (safe — not from URL)
    campaign_id = request.session.get('campaign_id')
    amount = request.session.get('amount')

    if not campaign_id or not amount:
        messages.error(request, "Session expired. Please try donating again.")
        return redirect('home')

    campaign = get_object_or_404(Campaign, id=campaign_id)

    # Store donation
    donation = Donation.objects.create(
        campaign=campaign,
        donor=request.user,
        amount=amount,
        order_id=order_id,
        payment_id=payment_id,
    )



    # Clear session
    del request.session['campaign_id']
    del request.session['amount']

    messages.success(request, "Thank you for your donation!")

    return render(request, 'campaigns/payment_success.html', {
        'donation': donation,
        'campaign': campaign,
        'payment_id': payment_id,
        'campaign': campaign,
        'amount': amount,
    })



# ---------------- LOGOUT ----------------
def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "Logged out successfully")
    return redirect('home')


#----------------- ABOUT ------------------
def about(request):
    return render(request, 'campaigns/about.html')


# ---------------- CREATE CAMPAIGN ----------------
@login_required
def create_campaign(request):
    if request.method == 'POST':
        form = CampaignForm(request.POST, request.FILES)

        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.creator = request.user
            campaign.save()
            messages.success(request, "Campaign created successfully!")
            return redirect('campaign_detail', campaign_id=campaign.id)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = CampaignForm()

    return render(request, 'campaigns/create_campaign.html', {'form': form})

#----------Profile----------

@login_required
def profile(request):
    return render(request, 'campaigns/profile.html')

from django.db.models import Sum, F

@login_required
@login_required
def dashboard(request):
    # Get user's campaigns
    campaigns = Campaign.objects.filter(creator=request.user).order_by('-created_at')
    
    # Summary stats
    total_campaigns = campaigns.count()
    total_donations = Donation.objects.filter(
    campaign__creator=request.user
).aggregate(total=Sum('amount'))['total'] or 0
    active_campaigns = campaigns.count()
    
    # Recent donations across all user's campaigns
    recent_donations = Donation.objects.filter(
        campaign__creator=request.user
    ).order_by('-donated_at')[:5]
    
    context = {
        'campaigns': campaigns[:5],  # Show top 5
        'total_campaigns': total_campaigns,
        'total_donations': total_donations,
        'active_campaigns': active_campaigns,
        'recent_donations': recent_donations,
    }
    
    return render(request, 'campaigns/dashboard.html', context)

@login_required
def my_campaigns(request):
    return render(request, 'campaigns/my_campaigns.html')

@login_required
def my_donations(request):
    donations = Donation.objects.filter(donor=request.user).order_by('-donated_at')

    return render(request, 'campaigns/my_donations.html', {
        'donations': donations
    })

@login_required
def my_campaigns(request):
    campaigns = Campaign.objects.filter(creator=request.user).order_by('-created_at')

    return render(request, 'campaigns/my_campaigns.html', {
        'campaigns': campaigns
    })

#----Edit Campaign----
@login_required
def edit_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    
    # Security: Only creator can edit
    if campaign.creator != request.user:
        messages.error(request, "You don't have permission to edit this campaign.")
        return redirect('home')
    
    if request.method == 'POST':
        form = CampaignForm(request.POST, request.FILES, instance=campaign)
        if form.is_valid():
            form.save()
            messages.success(request, "Campaign updated successfully!")
            return redirect('my_campaigns')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = CampaignForm(instance=campaign)
    
    return render(request, 'campaigns/edit_campaign.html', {
        'form': form,
        'campaign': campaign
    })

#----Delete----
@login_required
def delete_campaign(request, id):
    campaign = get_object_or_404(Campaign, id=id, creator=request.user)

    if request.method == 'POST':
        campaign.delete()
        return redirect('my_campaigns')

    return render(request, 'campaigns/delete_campaign.html', {'campaign': campaign})