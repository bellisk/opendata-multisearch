# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.conf import settings
from .models import Portal
from .query import query_portals
import json, re

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
        portals = [p for p in portals if str(p.id) in request.GET]
        c['portals'] = [{'portal': p, 'active': p in portals} for p in Portal.objects.all()]
        c['results'], top_results, c['portal_errors'] = query_portals(query_string, portals)
        c['narrowing_terms'] = extract_narrowing_terms(top_results, keyword_query)

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

    counttuples = [(k, v) for k, v in wordcounts.items() if len(k) > 4 and v > 1 and v < len(results) * 0.75]

    return [t[0] for t in sorted(counttuples, key=lambda t: -t[1])][:8]
