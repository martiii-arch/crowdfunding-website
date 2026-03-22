from django.db import models
from django.contrib.auth.models import User


class Campaign(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField()

    goal_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    amount_raised = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="campaigns"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    image = models.ImageField(
        upload_to='campaign_images/',
        blank=True,
        null=True
    )


    def progress(self):

        if self.goal_amount > 0:

            return (self.amount_raised / self.goal_amount) * 100

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
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    donated_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):

        return f"{self.donor.username} donated {self.amount}"