from django import forms
from .models import Group, GroupUser, Expense


class ExpenseForm(forms.ModelForm):
    paid_date = forms.DateTimeField(widget=forms.DateTimeInput(format='%Y-%m-%d %H:%M'))

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
        widgets = {
            'split_with': forms.CheckboxSelectMultiple(),
        }


class SettleUpForm(forms.ModelForm):
    paid_to = forms.ModelChoiceField(queryset=GroupUser.objects.all())

    class Meta:
        model = Expense
        fields = [
            'price',
            'paid_date',
            'paid_by',
            'paid_to',
        ]

        labels = {
            'price': 'Gave back',
        }


class GroupForm(forms.ModelForm):
    user_email = forms.EmailField()

    class Meta:
        model = Group
        fields = [
            'name',
            'user_email',
        ]

        labels = {
            'name': 'Group Name',
        }
