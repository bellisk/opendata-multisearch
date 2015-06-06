# -*- coding: utf-8 -*-

from django.shortcuts import render
from ord_hackday.search.models import Portal
import requests, json, re

def search(request):
    c = {}

    if 'query' in request.GET:
        query = request.GET['query']
        c['query'] = query
        portals = Portal.objects.all()
        c['portals'] = portals
        
        if len(query) > 0:
            c['results'] = []

            all_results = []
            for portal in portals:
                url = portal.url + '/api/3/action/package_search?q=' + query
                r = requests.get(url)
                json_result = json.loads(r.text)

                if json_result['success']:
                    all_results.extend(json_result['result']['results'])
                    for r in json_result['result']['results']:
                        r['result_url'] = portal.url + '/dataset/' + r['name']
                        c['results'].append(r)
            
            narrowing_terms = extract_narrowing_terms(all_results)
            c['narrowing_terms'] = narrowing_terms
    return render(request, 'search.html', c)

def extract_narrowing_terms(results):
    titles = [re.sub(r'[«»!?,.()\[\]]', ' ', r['title'].lower()) for r in results]
    wordcounts = {}
    for t in titles:
        for w in re.split(r' +', t):
            if not w in wordcounts:
                wordcounts[w] = 1
            else:
                wordcounts[w] += 1
    counttuples = [(k, v) for k, v in wordcounts.iteritems() if len(k) > 4 and v > 1 and v < len(results) * 0.75]
    return [t[0] for t in sorted(counttuples, key=lambda t: -t[1])][:8]
