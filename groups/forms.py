from django import forms
from .models import Expense
from django.core.exceptions import ValidationError


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            'title',
            'price',
            'paid_date',
            'paid_by',
            'split_with',
            'comment'
        ]


class SettleUpForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            'price',
            'paid_date',
            'paid_by',
            'split_with',
        ]

        labels = {
            'price': 'Gave back',
            'split_with': 'to'
        }

    def clean(self):
        data = super().clean()
        if data.get('split_with').count() != 1:
            raise ValidationError('You have to choose only 1 person to settle the balance!')
        return data
