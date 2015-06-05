from django.shortcuts import render
from ord_hackday.search.models import Portal
import requests
import json


def search(request):
    c = {}

    if 'query' in request.GET:
        query = request.GET['query']

        if len(query) > 0:
            portals = Portal.objects.all()
            c['portals'] = portals
            c['results'] = []

            for portal in portals:
                url = portal.url + '/api/3/action/package_search?q=' + query
                r = requests.get(url)
                json_result = json.loads(r.text)

                if json_result['success']:
                    for r in json_result['result']['results']:
                        c['results'].append(r)

    return render(request, 'search.html', c)