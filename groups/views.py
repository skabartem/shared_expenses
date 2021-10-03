from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.urls import reverse
from django.http import HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from groups.models import Group, GroupUser, Expense, ExpenseComment, TransferToMake, CashMovement
from .forms import ExpenseForm, SettleUpForm
from .utils import track_cash_movements


@method_decorator(login_required, name='dispatch')
class GroupDetailView(DetailView):
    model = Group
    template_name = 'groups/group.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        group = Group.objects.get(id=self.kwargs['pk'])

        context['group_expenses'] = Expense.objects.filter(group=group)
        context['group_users'] = GroupUser.objects.filter(group=group)
        context['cash_transfers'] = TransferToMake.objects.filter(group=group)
        context['group_data'] = group

        self.request.session['group_id'] = str(group.id)
        return context


@method_decorator(login_required, name='dispatch')
class GroupsListView(ListView):
    model = Group
    template_name = 'groups/user-groups.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_groups'] = Group.objects.filter(profile=self.request.user.profile)
        return context


@method_decorator(login_required, name='dispatch')
class GroupCreateView(CreateView):
    model = Group
    template_name = 'groups/create-group.html'

    fields = [
        'name',
        'group_users',
    ]

    def form_valid(self, form):
        group = form.save(commit=False)
        group.created_by = self.request.user.profile
        group.save()

        self.request.session['group_id'] = str(group.id)

        GroupUser.objects.create(
            balance=0,
            group=group,
            profile=group.created_by,
        )

        return super().form_valid(form)

    def get_success_url(self):
        group_id = self.request.session.get('group_id')
        return f'/groups/{group_id}'


@method_decorator(login_required, name='dispatch')
class ExpenseCreateView(CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'groups/expense.html'

    def get_form(self, *args, **kwargs):
        group_id = self.request.session.get('group_id')
        group = Group.objects.get(id=group_id)

        form = super().get_form(*args, **kwargs)
        group_users = GroupUser.objects.filter(group=group)
        # limit only to current group users
        form.fields['paid_by'].queryset = group_users
        form.fields['split_with'].queryset = group_users
        # pre_fill form
        form.fields['paid_by'].initial = GroupUser.objects.get(group=group, profile=self.request.user.profile)
        form.fields['split_with'].initial = group_users
        return form

    def post(self, request, **kwargs):
        expense_form = ExpenseForm(request.POST)
        group_id = self.request.session.get('group_id')
        group = Group.objects.get(id=group_id)
        if expense_form.is_valid():
            expense = expense_form.save(commit=False)
            expense.group = group
            expense.created_by = GroupUser.objects.get(group=group, profile=self.request.user.profile)

            if expense.comment:
                ExpenseComment.objects.create(
                    group=expense.group,
                    created_by=expense.created_by,
                    comment_text=expense.comment,
                    expense=expense
                )
                expense.comment = None
            expense.save()
            expense_form.save_m2m()

            track_cash_movements(expense, expense.split_with.all())

        return HttpResponseRedirect(reverse('detail', args=[str(expense.group.id)]))

    def get_success_url(self):
        group_id = self.request.session.get('group_id')
        return f'/groups/{group_id}'


class ExpenseUpdateView(UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'groups/expense.html'

    def get_form(self, *args, **kwargs):
        group_id = self.request.session.get('group_id')
        group = Group.objects.get(id=group_id)

        form = super().get_form(*args, **kwargs)
        group_users = GroupUser.objects.filter(group=group)
        # limit only to current group users
        form.fields['paid_by'].queryset = group_users
        form.fields['split_with'].queryset = group_users
        return form

    def form_valid(self, form):
        old_expense = Expense.objects.get(id=self.kwargs['pk'])
        old_price = old_expense.price
        old_lender = old_expense.paid_by
        old_borrowers = list(old_expense.split_with.all())

        expense = form.save(commit=False)
        expense.created_by = GroupUser.objects.get(group=expense.group, profile=self.request.user.profile)

        if expense.comment:
            ExpenseComment.objects.create(
                group=expense.group,
                created_by=expense.created_by,
                comment_text=expense.comment,
                expense=expense
            )
            expense.comment = None

        expense.save()
        form.save_m2m()

        '''
        CHECK IF THERE IS same_price, same_lander, same_borrowers AFTER THE UPDATE
        TO EVALUATE IF THE BALANCE RECALCULATION OF GROUP USERS IS REQUIRED
        '''
        same_price = expense.price == old_price
        same_lander = expense.paid_by == old_lender
        same_borrowers = list(expense.split_with.all()) == old_borrowers

        if not same_price or not same_lander or not same_borrowers:
            cash_movements = CashMovement.objects.filter(expense=old_expense)
            # revert balance changes caused by the expense
            for balance_change in cash_movements:
                balance_change.group_user.balance = balance_change.group_user.balance - balance_change.balance_impact
                balance_change.group_user.save()
                balance_change.delete()

            updated_borrowers = expense.split_with.all()

            track_cash_movements(expense, updated_borrowers)

        return HttpResponseRedirect(reverse('detail', args=[str(expense.group.id)]))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expense_comments'] = ExpenseComment.objects.filter(expense_id=self.kwargs['pk'])
        return context

    def get_success_url(self):
        group_id = self.request.session.get('group_id')
        return f'/groups/{group_id}'


@method_decorator(login_required, name='dispatch')
class ExpenseDeleteView(DeleteView):
    model = Expense

    def get_success_url(self):
        group_id = self.request.session.get('group_id')
        return f'/groups/{group_id}'


@method_decorator(login_required, name='dispatch')
class SettleUpView(CreateView):
    model = Expense
    form_class = SettleUpForm
    template_name = 'groups/settle-up.html'

    def get_form(self, *args, **kwargs):
        group_id = self.request.session.get('group_id')
        group = Group.objects.get(id=group_id)

        form = super().get_form(*args, **kwargs)
        group_users = GroupUser.objects.filter(group=group)
        # limit only to current group users
        form.fields['paid_by'].queryset = group_users
        form.fields['paid_to'].queryset = group_users
        # pre_fill form
        form.fields['paid_by'].initial = GroupUser.objects.get(group=group, profile=self.request.user.profile)
        return form

    def post(self, request, **kwargs):
        settlement_form = SettleUpForm(request.POST)
        group_id = self.request.session.get('group_id')
        group = Group.objects.get(id=group_id)

        if settlement_form.is_valid():
            settlement = settlement_form.save(commit=False)
            settlement.group = group
            settlement.created_by = GroupUser.objects.get(group=group, profile=self.request.user.profile)
            settlement.title = f'{settlement.paid_by} gave back {settlement.price}'

            paid_to = settlement_form.cleaned_data.get('paid_to')

            settlement.save()
            settlement.split_with.set([paid_to])
            settlement_form.save_m2m()

            track_cash_movements(settlement, settlement.split_with.all())

            return HttpResponseRedirect(reverse('detail', args=[str(settlement.group.id)]))

    def get_success_url(self):
        group_id = self.request.session.get('group_id')
        return f'/groups/{group_id}'
