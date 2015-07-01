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


def page_size(num_portals):
    return max(settings.MIN_PORTAL_RESULTS, settings.EXPECTED_PAGE_RESULTS // num_portals)


## Used for single-threaded querying.
class MockFuture:
    def __init__(self, query_string):
        self._result = requests.get(query_string)
    
    def result(self):
        return self._result

def start_query(session, query_string, portal, num_portals, page_number):
    query_string = portal.url + '/api/3/action/package_search?q=' + \
        query_string + \
        '&rows=' + str(page_size(num_portals) + 1) + \
        '&start=' + str(page_number * page_size(num_portals))
    if session:
        return (
            session.get(query_string),
            portal
        )
    else:
        return (
            MockFuture(query_string),
            portal
        )
        

def query_portals(query_string, portals, page_number):
    start = time.time()
    futures = [start_query(session, query_string, portal, len(portals), page_number) for portal in portals]
    results = []
    top_results = []
    errors = []
    more = False

    for future, portal in futures:
        try:
            r = future.result()
            json_result = json.loads(r.text)

            if json_result['success']:
                top_results.extend(json_result['result']['results'][:30])

                if len(json_result['result']['results']) > page_size(len(portals)):
                    more = True

                for r in json_result['result']['results']:
                    r['result_url'] = portal.url + '/dataset/' + r['name']
                    r['portal'] = portal
                    results.append(r)
        except ValueError as e:
            errors.append(portal)
            continue
    print("Time taken: " + str(time.time() - start))
    return (results, top_results, errors, more)
