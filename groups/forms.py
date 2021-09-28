from django.forms import ModelForm
from .models import Expense


class ExpenseCreateForm(ModelForm):
    class Meta:
        model = Expense
        fields = [
            'title',
            'price',
            'group',
            'paid_date',
            'paid_by',
            'split_with',
            'comment'
        ]
