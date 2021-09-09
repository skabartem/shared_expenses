from django.db.models.signals import post_save

from .models import GroupUser, Expense


def recalculate_balances_caused_by_expense(sender, instance, created, **kwargs):
    expense = instance
    split_with = GroupUser.objects.filter(group=expense.group)
    # update caused by added expense
    if not created:
        # pool previous expense price
        previous_price = True
        old_split_with = True
        if previous_price != expense.price and old_split_with == expense.split_with:
            pass
        elif previous_price == expense.price and old_split_with != expense.split_with:
            pass
        elif previous_price != expense.price and old_split_with != expense.split_with:
            pass
    # update caused by expense update
    elif created:
        split_amount = expense.price / len(split_with)
        for user in split_with:
            if user != expense.created_by:
                user.balance = round(user.balance - split_amount, 2)
            else:
                user.balance = round(user.balance + expense.price - split_amount, 2)
            user.save()


post_save.connect(recalculate_balances_caused_by_expense, sender=Expense)
