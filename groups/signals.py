from django.db.models.signals import post_save

from .models import GroupUser, Expense


def recalculate_balances_caused_by_expense(sender, instance, created, **kwargs):
    # update because of added expense
    if created:
        pass
    # update because of expense update
    elif not created:
        expense = instance
        split_with = GroupUser.objects.filter(group=expense.group)
        split_amount = expense.price / len(split_with)
        for user in split_with:
            if user != expense.created_by:
                user.balance = round(user.balance - split_amount, 2)
                user.save()
            else:
                user.balance = round(user.balance + split_amount * (len(split_with)-1), 2)
                user.save()


post_save.connect(recalculate_balances_caused_by_expense, sender=Expense)
