from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.urls import reverse
from django.http import HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from groups.models import Group, GroupUser, Expense, ExpenseComment, TransferToMake
from .forms import ExpenseCreateForm

from django.core.cache import cache


@method_decorator(login_required, name='dispatch')
class GroupDetailView(DetailView):
    model = Group
    template_name = 'groups/group.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group_expenses'] = Expense.objects.filter(group_id=self.kwargs['pk'])
        context['group_users'] = GroupUser.objects.filter(group_id=self.kwargs['pk'])
        context['group_data'] = Group.objects.get(id=self.kwargs['pk'])
        context['cash_transfers'] = TransferToMake.objects.filter(group_id=self.kwargs['pk'])

        # https://stackoverflow.com/questions/58883570/pass-data-between-different-views-in-django/58912197#58912197
        # change to REST when learnt
        cache.set('current_group', context['group_data'])
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

        cache.set('current_group', group.id)

        GroupUser.objects.create(
            balance=0,
            group=group,
            profile=group.created_by,
        )

        return super().form_valid(form)

    def get_success_url(self):
        if cache.get("current_group"):
            return f'/groups/{cache.get("current_group")}'


@method_decorator(login_required, name='dispatch')
class ExpenseCreateView(CreateView):
    model = Expense
    form_class = ExpenseCreateForm
    template_name = 'groups/expense.html'

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        group_users = GroupUser.objects.filter(group=cache.get('current_group'))
        # limit only to current group users
        form.fields['paid_by'].queryset = group_users
        form.fields['split_with'].queryset = group_users
        # pre_fill form
        current_group = group_users[0].group
        form.fields['group'].initial = current_group
        form.fields['paid_by'].initial = GroupUser.objects.get(group=current_group, profile=self.request.user.profile)
        form.fields['split_with'].initial = group_users
        return form

    def form_valid(self, form):
        expense = form.save(commit=False)
        expense.group = cache.get('current_group')
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

        return HttpResponseRedirect(reverse('detail', args=[str(expense.group.id)]))

    def get_success_url(self):
        if cache.get("current_group"):
            return f'/groups/{cache.get("current_group").id}'


@method_decorator(login_required, name='dispatch')
class ExpenseUpdateView(UpdateView):
    model = Expense
    form_class = ExpenseCreateForm
    template_name = 'groups/expense.html'

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        group_users = GroupUser.objects.filter(group=cache.get('current_group'))
        # limit only to current group users
        form.fields['paid_by'].queryset = group_users
        form.fields['split_with'].queryset = group_users
        return form

    def form_valid(self, form):
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

        return HttpResponseRedirect(reverse('detail', args=[str(expense.group.id)]))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expense_comments'] = ExpenseComment.objects.filter(expense_id=self.kwargs['pk'])
        return context

    def get_success_url(self):
        return f'/groups/{cache.get("current_group").id}'


@method_decorator(login_required, name='dispatch')
class ExpenseDeleteView(DeleteView):
    model = Expense

    def get_success_url(self):
        if cache.get("current_group"):
            return f'/groups/{cache.get("current_group").id}'
