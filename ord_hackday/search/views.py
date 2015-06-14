# -*- coding: utf-8 -*-

from django.shortcuts import render
from ord_hackday.search.models import Portal
import requests
import json
import re


def search(request):
    c = {}
    query_string = ''
    portals = Portal.objects.all()
    c['portals'] = portals

    # Construct query
    if 'query' in request.GET:
        query_string = request.GET['query']
        c['query'] = query_string

    pubfrom = request.GET['pubfrom'] + 'T00:00:00Z' if 'pubfrom' in request.GET and request.GET['pubfrom'] else ''
    pubto = request.GET['pubto'] + 'T23:59:59Z' if 'pubto' in request.GET and request.GET['pubto'] else ''
    pub_range = (' metadata_created:[%s TO %s]' % (pubfrom, pubto))
    
    if 'pubfrom' in request.GET:
        c['pubfrom'] = request.GET['pubfrom']
    if 'pubto' in request.GET:
        c['pubto'] = request.GET['pubto']

    if pubfrom or pubto:
        query_string = query_string + pub_range

    # Search with query
    if len(query_string) > 0:
        c['results'] = []
        c['portal_errors'] = []
        all_results = []

        for portal in portals:
            try:
                url = portal.url + '/api/3/action/package_search?q=' + query_string + '&rows=1000'
                r = requests.get(url)
                print url
                json_result = json.loads(r.text)

                if json_result['success']:
                    all_results.extend(json_result['result']['results'])
                    for r in json_result['result']['results']:
                        r['result_url'] = portal.url + '/dataset/' + r['name']
                        c['results'].append(r)

                narrowing_terms = extract_narrowing_terms(all_results)
                c['narrowing_terms'] = narrowing_terms
            except ValueError, e:
                c['portal_errors'].append(portal)
                continue

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
