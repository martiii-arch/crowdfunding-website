from django import forms
from .models import Campaign, Donation
from django.core.validators import MinValueValidator


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['title', 'description', 'goal_amount', 'image']

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter campaign title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your campaign...',
                'rows': 5
            }),
            'goal_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter goal amount in ₹',  # ✅ FIXED: ₹ not $
                'min': 1
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }

    def clean_goal_amount(self):
        amount = self.cleaned_data.get('goal_amount')
        if amount is None or amount <= 0:
            raise forms.ValidationError(
                "Goal amount must be greater than ₹0."
            )
        return amount

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if len(title) < 5:
            raise forms.ValidationError(
                "Title must be at least 5 characters long."
            )
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description', '').strip()
        if len(description) < 20:
            raise forms.ValidationError(
                "Description must be at least 20 characters long."
            )
        return description


class DonationForm(forms.Form):
    amount = forms.DecimalField(
        min_value=1,
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1)],
        widget=forms.NumberInput(attrs={
            'class': 'w-full border rounded-xl py-3 px-4 mt-1',
            'placeholder': 'Enter amount in ₹',
            'min': '1',
        })
    )

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None or amount <= 0:
            raise forms.ValidationError(
                "Please enter a valid donation amount greater than ₹0."
            )
        return amount