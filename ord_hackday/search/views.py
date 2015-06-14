# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.conf import settings
from ord_hackday.search.models import Portal
import requests
import json
import re


def search(request):
    c = {}
    keyword_query = ''
    query_string = ''
    portals = Portal.objects.all()
    c['portals'] = [{'portal': p, 'active': True} for p in portals]

    # Construct query
    if 'query' in request.GET:
        keyword_query = request.GET['query']
        query_string = keyword_query
        c['query'] = query_string

    pubfrom = request.GET['pubfrom'] + 'T00:00:00Z' if 'pubfrom' in request.GET and request.GET['pubfrom'] else ''
    pubto = request.GET['pubto'] + 'T23:59:59Z' if 'pubto' in request.GET and request.GET['pubto'] else ''
    pub_range = (' metadata_created:[%s TO %s]' % (pubfrom, pubto))
    
    if 'pubfrom' in request.GET:
        c['pubfrom'] = request.GET['pubfrom']
    if 'pubto' in request.GET:
        c['pubto'] = request.GET['pubto']

    if pubfrom or pubto:
        query_string += pub_range

    # Search with query
    if len(query_string) > 0:
        c['has_query'] = True
        c['results'] = []
        c['portal_errors'] = []
        top_results = []

        portals = [p for p in portals if str(p.id) in request.GET]
        c['portals'] = [{'portal': p, 'active': p in portals} for p in Portal.objects.all()]

        for portal in portals:
            try:
                url = portal.url + '/api/3/action/package_search?q=' + query_string + '&rows=' + str(settings.MAX_PORTAL_RESULTS)
                r = requests.get(url)
                json_result = json.loads(r.text)

                if json_result['success']:
                    top_results.extend(json_result['result']['results'][:30])
                    for r in json_result['result']['results']:
                        r['result_url'] = portal.url + '/dataset/' + r['name']
                        r['portal'] = portal
                        c['results'].append(r)

                narrowing_terms = extract_narrowing_terms(top_results, keyword_query)
                c['narrowing_terms'] = narrowing_terms
            except ValueError, e:
                c['portal_errors'].append(portal)
                continue

    return render(request, 'search.html', c)

def letters_only(s):
    return re.sub(r'[«»!?,.:;|@#&=+0()\[\]{}<>*+]', ' ', s.lower())

def extract_narrowing_terms(results, query):
    titles = [letters_only(r['title']) for r in results]
    used_keywords = set(re.split(' +', letters_only(query)))
    wordcounts = {}

    for t in titles:
        for w in re.split(r' +', t):
            if not w in used_keywords:
                if not w in wordcounts:
                    wordcounts[w] = 1
                else:
                    wordcounts[w] += 1

    counttuples = [(k, v) for k, v in wordcounts.iteritems() if len(k) > 4 and v > 1 and v < len(results) * 0.75]

    return [t[0] for t in sorted(counttuples, key=lambda t: -t[1])][:8]
