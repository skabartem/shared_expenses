from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import GroupUser, Expense, CashMovement, TransferToMake
from .utils import min_cash_flow_rec


def manage_transfers(group):
    TransferToMake.objects.filter(group=group).delete()
    grp_users = GroupUser.objects.filter(group=group)
    balances = [user.balance for user in grp_users]
    min_cash_flow_rec(grp_users, balances)


@receiver(post_save, sender=Expense)
def recalculate_balances_created_expense(sender, instance, created, **kwargs):
    if created:
        expense = instance
        split_with = GroupUser.objects.filter(group=expense.group)
        split_amount = round(expense.price / len(split_with), 2)

        lent = expense.price - split_amount if expense.paid_by in split_with else expense.price
        rounding_fix = round(split_amount + 0.01, 2) if expense.price % split_amount else 0

        for user in split_with:
            if rounding_fix and user != expense.paid_by:
                user.balance += -rounding_fix
                CashMovement.objects.create(group_user=user, expense=expense, balance_impact=rounding_fix)
                rounding_fix = 0
            elif user != expense.paid_by:
                user.balance += -split_amount
                CashMovement.objects.create(group_user=user, expense=expense, balance_impact=split_amount)
            user.save()

        expense.paid_by.balance += lent
        CashMovement.objects.create(group_user=expense.paid_by, expense=expense, balance_impact=lent)
        expense.paid_by.save()

        manage_transfers(expense.group)


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
