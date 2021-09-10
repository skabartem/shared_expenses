from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import GroupUser, Expense


@receiver(post_save, sender=Expense)
def recalculate_balances_caused_by_expense(sender, instance, created, **kwargs):
    expense = instance
    split_with = GroupUser.objects.filter(group=expense.group)
    # update caused by added expense
    if created:
        split_amount = expense.price / len(split_with)
        for user in split_with:
            if user != expense.paid_by:
                user.balance = round(user.balance - split_amount, 2)
            else:
                user.balance = round(user.balance + expense.price - split_amount, 2)
            user.save()
    # update caused by expense update
    else:
        # pool previous expense price
        previous_price = True
        old_split_with = True
        if previous_price != expense.price and old_split_with == expense.split_with:
            pass
        elif previous_price == expense.price and old_split_with != expense.split_with:
            pass
        elif previous_price != expense.price and old_split_with != expense.split_with:
            pass
