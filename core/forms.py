from django import forms
from .models import Deposit, Withdrawal, Cryptocurrency
from django.contrib.auth import get_user_model

User = get_user_model()

class DepositForm(forms.ModelForm):
    class Meta:
        model = Deposit
        fields = ['cryptocurrency', 'amount']
        widgets = {
            'cryptocurrency': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')

        # Additional validation: Ensure the deposit amount is positive
        if amount <= 0:
            raise forms.ValidationError("Deposit amount must be greater than zero.")

        return cleaned_data

class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = Withdrawal
        fields = ['cryptocurrency', 'amount', 'destination_address']

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')

        if amount <= 0:
            raise forms.ValidationError("Withdrawal amount must be greater than zero.")
        return cleaned_data