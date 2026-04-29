from django.shortcuts import render, get_object_or_404, redirect
from .models import Campaign, Donation
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
import razorpay


# ---------------- HOME ----------------
def home(request):
    campaigns = Campaign.objects.all()[:6]

    for c in campaigns:
        total = Donation.objects.filter(campaign=c).aggregate(total=Sum('amount'))['total'] or 0
        c.amount_raised = total

        c.progress = (total / c.goal_amount) * 100 if c.goal_amount > 0 else 0

    return render(request, 'campaigns/home.html', {
        'campaigns': campaigns
    })


# ---------------- CAMPAIGN DETAIL ----------------
def campaign_detail(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    total = Donation.objects.filter(campaign=campaign).aggregate(total=Sum('amount'))['total'] or 0
    campaign.amount_raised = total

    campaign.progress = (total / campaign.goal_amount) * 100 if campaign.goal_amount > 0 else 0

    donations = Donation.objects.filter(
        campaign=campaign
    ).order_by('-donated_at')[:5]

    return render(request, 'campaigns/campaign_detail.html', {
        'campaign': campaign,
        'donations': donations
    })


# ---------------- EXPLORE ----------------
def explore(request):
    campaigns = Campaign.objects.all()

    for c in campaigns:
        total = Donation.objects.filter(campaign=c).aggregate(total=Sum('amount'))['total'] or 0
        c.amount_raised = total

        c.progress = (total / c.goal_amount) * 100 if c.goal_amount > 0 else 0

    return render(request, 'campaigns/explore.html', {
        'campaigns': campaigns
    })


# ---------------- LOGIN ----------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, "Login successful")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'campaigns/login.html')


# ---------------- REGISTER ----------------
def register(request):
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

        user = User.objects.create_user(username=username, email=email, password=password)

        login(request, user)
        messages.success(request, "Account created successfully")
        return redirect('home')

    return render(request, 'campaigns/register.html')


# ---------------- DONATE ----------------
@login_required
def donate(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    if request.method == "POST":
        amount_rupees = int(request.POST.get("amount"))
        amount_paise = amount_rupees * 100

        # ✅ STORE IN SESSION
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

        return render(request, "campaigns/payment.html", {
            "campaign": campaign,
            "order_id": order["id"],
            "amount": amount_paise,
            "razorpay_key": settings.RAZORPAY_KEY_ID
        })

    return render(request, 'campaigns/donation_page.html', {
        'campaign': campaign
    })


# ---------------- PAYMENT SUCCESS ----------------
@csrf_exempt
@login_required
def payment_success(request):
    payment_id = request.POST.get("razorpay_payment_id")

    # ✅ GET FROM SESSION (RELIABLE)
    campaign_id = request.session.get('campaign_id')
    amount = request.session.get('amount')

    if campaign_id and amount:
        campaign = get_object_or_404(Campaign, id=campaign_id)

        Donation.objects.create(
            campaign=campaign,
            donor=request.user,
            amount=amount
        )

        # OPTIONAL: clear session
        del request.session['campaign_id']
        del request.session['amount']

    return render(request, 'campaigns/payment_success.html', {
        'payment_id': payment_id
    })


# ---------------- LOGOUT ----------------
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('home')


# ---------------- CREATE CAMPAIGN ----------------
from .forms import CampaignForm

@login_required
def create_campaign(request):
    if request.method == 'POST':
        form = CampaignForm(request.POST, request.FILES)

        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.creator = request.user
            campaign.save()

            messages.success(request, "Campaign created successfully")
            return redirect('home')
    else:
        form = CampaignForm()

    return render(request, 'campaigns/create_campaign.html', {'form': form})