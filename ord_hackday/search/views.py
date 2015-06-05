from django.shortcuts import render


def search(request, query=''):
    c = {}

    return render(request, 'search.html', c)