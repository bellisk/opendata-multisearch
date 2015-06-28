# -*- coding: utf-8 -*-

from django.conf import settings
import requests, json
from requests_futures.sessions import FuturesSession


mock = True
session = FuturesSession()

class MockFuture:
    def __init__(self, query_string, portal):
        print(portal.url + '/api/3/action/package_search?q=' + query_string + '&rows=' + str(settings.MAX_PORTAL_RESULTS))
        self._result = requests.get(portal.url + '/api/3/action/package_search?q=' + query_string + '&rows=' + str(settings.MAX_PORTAL_RESULTS))
    
    def result(self):
        return self._result

def start_query(session, query_string, portal):
    if mock:
        return (
            MockFuture(query_string, portal),
            portal
        )
    else:
        return (
            session.get(portal.url + '/api/3/action/package_search?q=' + query_string + '&rows=' + str(settings.MAX_PORTAL_RESULTS)),
            portal
        )

def query_portals(query_string, portals):
    futures = [start_query(session, query_string, portal) for portal in portals]
    results = []
    top_results = []
    errors = []
    for future, portal in futures:
        try:
            r = future.result()
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
