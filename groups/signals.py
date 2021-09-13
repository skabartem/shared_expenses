from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import GroupUser, Expense


@receiver(post_save, sender=Expense)
def recalculate_balances_created_expense(sender, instance, created, **kwargs):
    if created:
        expense = instance
        split_with = GroupUser.objects.filter(group=expense.group)
        split_amount = expense.price / len(split_with)
        for user in split_with:
            if user != expense.paid_by:
                user.balance = round(user.balance - split_amount, 2)
            else:
                user.balance = round(user.balance + expense.price - split_amount, 2)
            user.save()


@receiver(pre_save, sender=Expense)
def recalculate_balances_updated_expense(sender, instance, **kwargs):
    if instance.id is None:
        updated_expense = instance
        prev_expense = Expense.objects.get(id=updated_expense.id)
        if updated_expense.price == prev_expense.price and \
                updated_expense.paid_by == prev_expense.paid_by and \
                updated_expense.split_with == prev_expense.split_with:
            print('NO CHANGES')
        else:
            print('RECALCULATION NEEDED')
