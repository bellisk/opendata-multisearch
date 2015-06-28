# -*- coding: utf-8 -*-

from django.conf import settings
import requests, json

def query_portals(query_string, portals):
    results = []
    top_results = []
    errors = []
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
                    results.append(r)
        except ValueError as e:
            errors.append(portal)
            continue
    return (results, top_results, errors)
