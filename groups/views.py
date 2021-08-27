from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView

from django.urls import reverse_lazy

from groups.models import Group, Expense


class GroupDetailView(DetailView):
    model = Group
    template_name = 'groups/group.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group_expenses'] = Expense.objects.filter(group_id=self.kwargs['pk'])
        return context


class GroupsListView(ListView):
    model = Group
    template_name = 'groups/user-groups.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_groups'] = Group.objects.filter(profile=self.request.user.profile)
        return context


class ExpenseCreateView(CreateView):
    model = Expense
    template_name = 'groups/expense.html'

    fields = [
        'title',
        'price',
        'paid_date',
        'split_with',
        'comment'
    ]

    def get_success_url(self):
        return reverse_lazy('user-groups')


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

    def get_success_url(self):
        return reverse_lazy('user-groups')
