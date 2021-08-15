from django.shortcuts import render


def profile_details(request):
    context = {}
    return render(request, 'users/details.html', context)
