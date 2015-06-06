from django.shortcuts import render
from ord_hackday.search.models import Portal
from ord_hackday.search import findtext
import requests, re, json

with open("placenames_ch.txt") as f:
    places = [" " + p[:-1] + " " for p in f if 30 > len(p) > 3]

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
                        r['result_url'] = portal.url + '/dataset/' + r['name']
                        r['notes'] += " --- " + ", ".join(find_places(r['title'] + " " + r['notes']))
                        c['results'].append(r)

    return render(request, 'search.html', c)

def find_places(text):
    text = " " + re.sub(r'[,.!?\[\]():/"]', ' ', text) + " "
    return [p.decode('UTF-8') for p in places if p in text.encode('UTF-8')]
