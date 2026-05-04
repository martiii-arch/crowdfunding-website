from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models import Sum


class Campaign(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField()

    goal_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1)]  
    )

    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="campaigns"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    image = models.ImageField(
        upload_to='campaign_images/',
        blank=True,
        null=True
    )

    # amount_raised is calculated dynamically
    @property
    def amount_raised(self):
        total = self.donations.aggregate(Sum('amount'))['amount__sum']
        return total or 0

    #  progress capped at 100 
    @property
    def progress(self):
        if self.goal_amount > 0:
            raw = (self.amount_raised / self.goal_amount) * 100
            return min(int(raw), 100)
        return 0

    def donor_count(self):
        return self.donations.count()

    def __str__(self):
        return self.title


class Donation(models.Model):

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="donations"
    )

    donor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="donations"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1)]
    )

    order_id = models.CharField(max_length=255, null=True, blank=True)
    payment_id = models.CharField(max_length=255, null=True, blank=True)

    donated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        donor_name = self.donor.username if self.donor else "Deleted user"
        return f"{donor_name} donated ₹{self.amount}"