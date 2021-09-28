from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from .models import GroupUser, Expense, CashMovement, TransferToMake
from .utils import min_cash_flow_rec


def manage_transfers(group):
    TransferToMake.objects.filter(group=group).delete()
    grp_users = GroupUser.objects.filter(group=group)
    balances = [user.balance for user in grp_users]
    min_cash_flow_rec(grp_users, balances)


# signal CALLED BEFORE updated expense data pushed to DB
@receiver(pre_save, sender=Expense)
def revert_previous_expense_changes(sender, instance, **kwargs):
    if not instance._state.adding:
        updated_expense = instance
        prev_expense = Expense.objects.get(id=updated_expense.id)

        same_price = updated_expense.price == prev_expense.price
        same_lander = updated_expense.paid_by == prev_expense.paid_by
        same_borrowers = updated_expense.split_with == prev_expense.split_with

        if not same_price or not same_lander or not same_borrowers:
            cash_movements = CashMovement.objects.filter(expense=prev_expense)

            # revert balance changes caused by the expense
            for balance_change in cash_movements:
                balance_change.group_user.balance = balance_change.group_user.balance - balance_change.balance_impact
                balance_change.group_user.save()
                balance_change.delete()


# signal CALLED AFTER updated expense data pushed to DB
@receiver(post_save, sender=Expense)
def recalculate_group_balances(sender, instance, created, **kwargs):
    expense = instance
    split_with = GroupUser.objects.filter(group=expense.group)
    split_amount = round(expense.price / len(split_with), 2)

    lent = round(expense.price - split_amount, 2) if expense.paid_by in split_with else round(expense.price, 2)
    if expense.price % split_amount:
        last_split = round(expense.price - split_amount * (len(split_with) - 1), 2)
    else:
        last_split = 0

    for user in split_with:
        if last_split and user != expense.paid_by:
            user.balance = round(user.balance - last_split, 2)
            CashMovement.objects.create(group_user=user, expense=expense, balance_impact=-last_split)
            last_split = 0
        elif user != expense.paid_by:
            user.balance = round(user.balance - split_amount, 2)
            CashMovement.objects.create(group_user=user, expense=expense, balance_impact=-split_amount)
        user.save()

    lender = GroupUser.objects.get(id=expense.paid_by.id)
    lender.balance = round(lender.balance + lent, 2)
    CashMovement.objects.create(group_user=expense.paid_by, expense=expense, balance_impact=lent)
    lender.save()

    manage_transfers(expense.group)


@receiver(pre_delete, sender=Expense)
def delete_expense(sender, instance, **kwargs):
    expense = instance
    cash_movements = CashMovement.objects.filter(expense=expense)
    for balance_change in cash_movements:
        balance_change.group_user.balance = balance_change.group_user.balance - balance_change.balance_impact
        balance_change.group_user.save()
        balance_change.delete()

    manage_transfers(expense.group)
