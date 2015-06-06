from django.shortcuts import render
import datetime
from ord_hackday.search.models import Portal
import requests
import json


def search(request):
    c = {}
    query_string = ''

    # Construct query
    if 'query' in request.GET:
        query_string = request.GET['query']

    pubfrom = request.GET['pubfrom'] + 'T00:00:00Z' if 'pubfrom' in request.GET else ''
    pubto = request.GET['pubto'] + 'T23:59:59Z' if 'pubto' in request.GET else ''
    pub_range = ('metadata_created:[%s TO %s]' % (pubfrom, pubto))

    if pubfrom or pubto:
        query_string = query_string + pub_range

    # Search with query
    if len(query_string) > 0:
        portals = Portal.objects.all()
        c['portals'] = portals
        c['results'] = []

        for portal in portals:
            url = portal.url + '/api/3/action/package_search?q=' + query_string
            r = requests.get(url)
            json_result = json.loads(r.text)

            if json_result['success']:
                for r in json_result['result']['results']:
                    r['result_url'] = portal.url + '/dataset/' + r['name']
                    c['results'].append(r)

    return render(request, 'search.html', c)
