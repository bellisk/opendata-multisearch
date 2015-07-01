# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.utils.http import urlencode
from .models import Portal
from .query import query_portals
import re


def search(request):
    portals = Portal.objects.all()
    search_params = (
        ('query',),
        ('pubfrom',),
        ('pubto',),
        ('page_number', '0'),
    ) + tuple([(p.id, 'on') for p in portals])

    c = {}
    keyword_query = ''
    query_string = ''

    # Construct query
    if 'query' in request.GET:
        keyword_query = request.GET['query']
        query_string = keyword_query
        c['query'] = query_string

    pubfrom = request.GET['pubfrom'] + 'T00:00:00Z' if 'pubfrom' in request.GET and request.GET['pubfrom'] else ''
    pubto = request.GET['pubto'] + 'T23:59:59Z' if 'pubto' in request.GET and request.GET['pubto'] else ''
    pub_range = (' metadata_created:[%s TO %s]' % (pubfrom, pubto))

    for param in search_params:
        if param[0] in request.GET:
            c[param[0]] = request.GET[param[0]]
        elif len(param) == 2:
            c[param[0]] = param[1]

    c['portals'] = [{'portal': p, 'active': c[p.id] == "on"} for p in portals]

    if pubfrom or pubto:
        query_string += pub_range

    # Search with query
    if len(query_string) > 0:
        c['has_query'] = True
        portals = [p for p in portals if str(p.id) in request.GET]
        c['portals'] = [{'portal': p, 'active': p in portals} for p in Portal.objects.all()]
        c['results'], top_results, c['portal_errors'], more = query_portals(query_string, portals, int(c['page_number']))
        c['narrowing_terms'] = extract_narrowing_terms(top_results, keyword_query)
        if int(c['page_number']) > 0:
            c['prev_get_params'] = get_params(c, search_params, page_number=str(int(c['page_number']) - 1))
        if more:
            c['next_get_params'] = get_params(c, search_params, page_number=str(int(c['page_number']) + 1))
        c['page_number_plus_one'] = str(int(c['page_number']) + 1)

    return render(request, 'search.html', c)

def get_params(c, search_params, **kwargs):
    c = dict(c)
    c.update(kwargs)
    return urlencode({p[0]: c[p[0]] for p in search_params})

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
