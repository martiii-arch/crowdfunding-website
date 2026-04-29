from django import forms
from .models import Campaign

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
                'placeholder': 'Describe your campaign...'
            }),
            'goal_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter goal amount'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }