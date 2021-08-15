from django.shortcuts import render


def your_groups(request):
    context = {}
    return render(request, 'groups/group.html', context)
