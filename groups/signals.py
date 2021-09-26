from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import GroupUser, Expense, CashMovement


@receiver(post_save, sender=Expense)
def recalculate_balances_created_expense(sender, instance, created, **kwargs):
    expense = instance
    split_with = GroupUser.objects.filter(group=expense.group)
    split_amount = expense.price / len(split_with)
    for user in split_with:
        if user != expense.paid_by:
            CashMovement.objects.create(group_user=user, expense=expense, balance_impact=-split_amount)
            user.balance = round(user.balance - split_amount, 2)
        else:
            lent = expense.price - split_amount
            CashMovement.objects.create(group_user=user, expense=expense, balance_impact=lent)
            user.balance = round(user.balance + lent, 2)
        user.save()


@receiver(pre_save, sender=Expense)
def recalculate_balances_updated_expense(sender, instance, **kwargs):
    if not instance._state.adding:
        updated_expense = instance
        prev_expense = Expense.objects.get(id=updated_expense.id)

        same_price = updated_expense.price == prev_expense.price
        same_lander = updated_expense.paid_by == prev_expense.paid_by
        same_borrowers = updated_expense.split_with == prev_expense.split_with

        if not same_price or not same_lander or not same_borrowers:
            impacted_users = CashMovement.objects.filter(expense=prev_expense)

            # revert balance changes caused by the expense
            for impact in impacted_users:
                impact.group_user.balance = impact.group_user.balance - impact.balance_impact
                impact.group_user.save()
                impact.delete()
