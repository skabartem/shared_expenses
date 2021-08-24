from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from groups.models import Group


class GroupDetailView(DetailView):
    model = Group
    template_name = 'groups/group.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['test'] = 'test_html'
        return context


class GroupsListView(ListView):
    model = Group
    template_name = 'groups/user-groups.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_groups'] = Group.objects.filter(profile=self.request.user.profile)
        return context
