# -*- coding: utf-8 -*-

from django.conf import settings
import requests, json, time


session = None

if settings.SIMULTANEOUS_QUERY_THREADS > 1:
    try:
        from requests_futures.sessions import FuturesSession
        from concurrent.futures import ThreadPoolExecutor
        session = FuturesSession(executor=ThreadPoolExecutor(max_workers=settings.SIMULTANEOUS_QUERY_THREADS))
    except:
        print("Unable to create thread pool for requests_futures. Falling back to synchronous querying.")


## Used for single-threaded querying.
class MockFuture:
    def __init__(self, query_string, portal):
        self._result = requests.get(portal.url + '/api/3/action/package_search?q=' + query_string + '&rows=' + str(settings.MAX_PORTAL_RESULTS))
    
    def result(self):
        return self._result

def start_query(session, query_string, portal):
    if session:
        return (
            session.get(portal.url + '/api/3/action/package_search?q=' + query_string + '&rows=' + str(settings.MAX_PORTAL_RESULTS)),
            portal
        )
    else:
        return (
            MockFuture(query_string, portal),
            portal
        )
        

def query_portals(query_string, portals):
    start = time.time()
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
    print("Time taken: " + str(time.time() - start))
    return (results, top_results, errors)
