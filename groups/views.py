from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView

from django.urls import reverse_lazy

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from groups.models import Group, GroupUser, Expense, ExpenseComment
from users.models import Profile

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
        response = super().form_valid(form)
        group = form.save(commit=False)
        group.created_by = self.request.user.profile

        GroupUser.objects.create(
            balance=0,
            group=group,
            profile=self.request.user.profile
        )

        group.save()
        return response

    def get_success_url(self):
        if cache.get("current_group"):
            return f'/groups/{cache.get("current_group").id}'


@method_decorator(login_required, name='dispatch')
class ExpenseCreateView(CreateView):
    model = Expense
    template_name = 'groups/expense.html'

    fields = [
        'title',
        'price',
        'group',
        'paid_date',
        'paid_by',
        'split_with',
        'comment'
    ]

    def form_valid(self, form):
        response = super().form_valid(form)
        expense = form.save(commit=False)
        expense.group = cache.get('current_group')
        expense.created_by = GroupUser.objects.get(group=expense.group, profile=self.request.user.profile)

        if expense.comment:
            ExpenseComment.objects.create(
                group=expense.group,
                created_by=GroupUser.objects.get(group=expense.group, profile=self.request.user.profile),
                comment_text=expense.comment,
                expense=expense
            )

        expense.save()
        return response

    def get_success_url(self):
        if cache.get("current_group"):
            return f'/groups/{cache.get("current_group").id}'


@method_decorator(login_required, name='dispatch')
class ExpenseUpdateView(UpdateView):
    model = Expense
    template_name = 'groups/expense.html'

    fields = [
        'title',
        'price',
        'paid_date',
        'split_with',
        'comment'
    ]

    def form_valid(self, form):
        response = super().form_valid(form)
        # TO FIX - FIRST TIME THE SIGNAL RAISES
        expense = form.save(commit=False)
        expense.created_by = GroupUser.objects.get(profile=self.request.user.profile)

        if expense.comment:
            ExpenseComment.objects.create(
                group=cache.get('current_group'),
                created_by=GroupUser.objects.get(profile=self.request.user.profile),
                comment_text=expense.comment,
                expense=expense
            )
        # TO FIX - SECOND TIME THE SIGNAL RAISES
        expense.save()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expense_comments'] = ExpenseComment.objects.filter(expense_id=self.kwargs['pk'])
        return context

    def get_success_url(self):
        return f'/groups/{cache.get("current_group").id}'
